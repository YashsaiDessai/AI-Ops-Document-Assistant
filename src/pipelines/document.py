from pathlib import Path
from typing import Optional

from src.ingestion.loaders import get_loader
from src.chunking.recursive import RecursiveCharacterChunker
from src.llm.client import LLMClientManager
from src.extraction.orchestrator import ExtractionOrchestrator
from src.models.extraction import FinalReport
from src.utils.formatter import to_markdown, to_json, save_report
from src.core.logging import get_logger
from src.core.exceptions import AppError

logger = get_logger(__name__)


class DocumentPipeline:
    """
    Coordinates the end-to-end document processing pipeline.
    Runs parsing, chunking, structured extraction, and report output serialization.
    """
    def __init__(self, client_manager: Optional[LLMClientManager] = None):
        self.client_manager = client_manager or LLMClientManager()

    async def run(
        self, 
        filepath: Path, 
        output_dir: Optional[Path] = None, 
        chunk_size: Optional[int] = None
    ) -> FinalReport:
        """
        Runs the full document parsing and extraction workflow.

        Args:
            filepath: Path to the input document.
            output_dir: Directory where generated reports will be stored.
            chunk_size: Optional override for the token chunking size.
        """
        logger.info("Initializing AI Ops Document execution pipeline", source_file=filepath.name)

        # 1. Ingestion Phase
        loader = get_loader(filepath)
        pages = loader.load(filepath)
        if not pages:
            raise AppError(f"Document ingestion failed: no readable text found in '{filepath.name}'")
        
        logger.info("Ingestion phase completed", total_pages=len(pages))

        # 2. Text Chunking Phase
        resolved_chunk_size = chunk_size or self.client_manager.settings.chunk_size
        chunker = RecursiveCharacterChunker(max_chunk_size=resolved_chunk_size)
        chunks = chunker.split_pages(pages, filepath.name)
        if not chunks:
            raise AppError("Chunking phase failed: zero text chunks produced.")

        logger.info("Chunking phase completed", total_chunks=len(chunks), size_limit=resolved_chunk_size)

        # 3. AI Extraction Phase (Map-Reduce concurrent jobs)
        orchestrator = ExtractionOrchestrator(self.client_manager)
        analyses = await orchestrator.run_map_phase(chunks)
        final_report = await orchestrator.run_reduce_phase(analyses)

        # 4. Report Serialization and Persistence
        # Resolve output directories: write next to input if output_dir is omitted
        if output_dir:
            out_dir_path = Path(output_dir)
            out_dir_path.mkdir(parents=True, exist_ok=True)
            report_md_path = out_dir_path / f"{filepath.stem}_report.md"
            report_json_path = out_dir_path / f"{filepath.stem}_report.json"
        else:
            report_md_path = filepath.parent / f"{filepath.stem}_report.md"
            report_json_path = filepath.parent / f"{filepath.stem}_report.json"

        # Save Markdown Report
        markdown_content = to_markdown(final_report)
        save_report(markdown_content, report_md_path)

        # Save JSON Report
        json_content = to_json(final_report)
        save_report(json_content, report_json_path)

        logger.info(
            "AI Ops Document Pipeline execution completed successfully",
            markdown_report=str(report_md_path),
            json_report=str(report_json_path)
        )
        return final_report
