import asyncio
from typing import List
from src.llm.client import LLMClientManager
from src.models.chunk import DocumentChunk
from src.models.extraction import ChunkAnalysis, FinalReport
from src.core.logging import get_logger
from src.core.exceptions import ExtractionError

logger = get_logger(__name__)


class ExtractionOrchestrator:
    """
    Coordinates the concurrent analysis of document chunks (Map phase) 
    and the synthesis of those analysis chunks into a unified report (Reduce phase).
    """
    def __init__(self, client_manager: LLMClientManager, max_concurrency: int = 5):
        self.client_manager = client_manager
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def _analyze_chunk_sem(self, chunk: DocumentChunk, chunk_index: int) -> ChunkAnalysis:
        """
        Helper method that invokes the LLM API under a concurrency throttle (semaphore).
        """
        async with self.semaphore:
            logger.info(
                "Analyzing document chunk", 
                chunk_id=chunk.chunk_id, 
                chunk_index=chunk_index,
                page_start=chunk.metadata.page_start,
                page_end=chunk.metadata.page_end
            )

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert AI Ops Analyst. Extract a concise summary, key entities, and "
                        "structured actionable tasks from the provided internal document segment."
                    )
                },
                {
                    "role": "user",
                    "content": f"Document segment content:\n\n{chunk.content}"
                }
            ]

            try:
                result = await self.client_manager.aparse_completion(
                    messages=messages,
                    response_format=ChunkAnalysis
                )
                logger.info(
                    "Completed analysis for chunk", 
                    chunk_id=chunk.chunk_id, 
                    chunk_index=chunk_index,
                    actions_extracted=len(result.action_items)
                )
                return result
            except Exception as e:
                # Return partial success fallback rather than crashing the whole process
                logger.error(
                    "Failed to process chunk, compiling error fallback", 
                    chunk_id=chunk.chunk_id, 
                    chunk_index=chunk_index,
                    error=str(e)
                )
                return ChunkAnalysis(
                    summary=f"[Extraction failure on chunk index {chunk_index} due to api error: {e}]",
                    action_items=[],
                    key_entities=[]
                )

    async def run_map_phase(self, chunks: List[DocumentChunk]) -> List[ChunkAnalysis]:
        """
        Executes concurrent chunk extraction across the entire document.
        """
        logger.info("Beginning Map Phase: analyzing chunks concurrently", total_chunks=len(chunks))
        tasks = [
            self._analyze_chunk_sem(chunk, idx)
            for idx, chunk in enumerate(chunks)
        ]
        results = await asyncio.gather(*tasks)
        return results

    async def run_reduce_phase(self, analyses: List[ChunkAnalysis]) -> FinalReport:
        """
        Aggregates and synthesizes chunk analysis results into a single cohesive report.
        """
        logger.info("Beginning Reduce Phase: synthesizing report from chunk results")
        
        combined_summaries = "\n".join([f"- {a.summary}" for a in analyses])
        
        # Build textual representation of all actions for synthesis input
        action_strings = []
        for a in analyses:
            for item in a.action_items:
                owner_str = f" (Owner: {item.owner})" if item.owner else ""
                action_strings.append(f"- [{item.priority}] {item.description}{owner_str}")
        
        all_actions_str = "\n".join(action_strings) if action_strings else "No raw action items detected."

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Technical Writer. Consolidate the provided segment summaries into a cohesive "
                    "executive summary for the entire document. Deduplicate and clean up the list of action items, "
                    "standardizing tasks while preserving critical technical details (such as deadlines or priority levels)."
                )
            },
            {
                "role": "user",
                "content": f"Segment Summaries:\n{combined_summaries}\n\nRaw Action Items:\n{all_actions_str}"
            }
        ]

        try:
            report = await self.client_manager.aparse_completion(
                messages=messages,
                response_format=FinalReport
            )
            logger.info("Successfully synthesized final report", consolidated_actions=len(report.consolidated_action_items))
            return report
        except Exception as e:
            logger.error("Failed to synthesize report during Reduce Phase", error=str(e))
            raise ExtractionError(f"Report synthesis failed: {e}") from e
