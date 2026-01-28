import logging
from typing import List, Optional
from pydantic import BaseModel,Field
from openai import OpenAI

from src.config import settings 

logger = logging.getLogger(__name__)

class ActionItem(BaseModel):
    """
    Schema for a single extracted task.
    """
    description : str = Field(..., description = "Concise description of the task")
    priority : str = Field(..., description = "High, Medium, or Low based on urgency")
    owner : Optional[str] = Field(None, description = "Person or department responsible, if mentioned")

class ChunkAnalysis(BaseModel):
    """
    The structured output expected from the LLM for a single chunk.
    """
    summary : str = Field(..., description = "3-5 sentence summary of this specific section")
    action_items : List[ActionItem] = Field(default_factory = list , description = "List of tasks found in this section")
    key_entities : List[str] = Field(default_factory = list, description = "Important names , dates , or systems mentioned")

class FinalReport(BaseModel):
    """
   The final aggregated report structure.
    """
    executive_summary : str
    consolidated_action_items : List[ActionItem]

client = OpenAi(api_key = settings.openai_api_key.get_secret_value())

def analyze_chunk(text_chunk : str, chunk_index : int) -> ChunkAnalysis :
    """
    Sends a single text chunk to the LLM to extract structured data.
    """
    logger.info(f"Analyzing chunk {} ({len(text_chunk)} chars)...")

    try:
        completion = client.beta.chat.completions.parse(
            model=settings.model_name,
            messages =[
                {"role": "system","content" : "You are an expert AI Ops Analyst. Extract a concise summary and actionable tasks from the provided internal document segment."},
                {"role": "user", "content" : f"Analyze this text:\n\n{text_chunk}"},
            ],
            response_format=ChunkAnalysis
        )

        result = completion.choices.message.parsed
        logger.debug(f"Chunk {chunk_index} analysis complete : {len(result.action_items)} actions found")
        return result

    except Exception as e:
        logger.error(f"Failed to process chunk {chunk_index} : {e}")
        return ChunkAnalysis(summary="Error processing chunk", action_items = [])

def sysnthesize_report(analyses : List[ChunkAnalysis]) -> FinalReport :
    """
    Combines multiple chunk analyses into one final coherent report.
    """
    logger.info("Sysnthesizing final report from chunk data...")

    combined_summaries = "\n".join([f"- {a.summary}" for a in analyses])

    all_actions = [item for a in analyses for item in a.action_items]

    try:
        completion = client.beta.chat.completions.parse(
            model = settings.model_name,
            messages = [
                {"role" : "system", "content","You are a Technical Writer. Consolidate the provided points into a cohesive executive summary and deduplicate the action items."}
                {"role" : "user", "content" : f"Summeries : \n{combined_summaries}\n\nRaw Actions : \n{all_actions}"},
            ],
            response_format = FinalReport,
        )
        return completion.choices.message.parsed

    except Exception as e:
        logger.error(f"Failed to synthesize report : {e}")
        return FinalReport(executive_summary = "Synthesis failed", consolidated_action_items = [])

