from pydantic import BaseModel, Field
from typing import List, Optional


class ActionItem(BaseModel):
    """
    Schema representing a single actionable task extracted from the document.
    """
    description: str = Field(..., description="Concise, clear description of the task or directive")
    priority: str = Field(
        ..., 
        description="Priority level: High, Medium, or Low. Determined based on urgency and severity."
    )
    owner: Optional[str] = Field(
        None, 
        description="Person, team, or department responsible for this task, if explicitly mentioned."
    )


class ChunkAnalysis(BaseModel):
    """
    Structured extraction schema expected from the LLM for an individual text chunk.
    """
    summary: str = Field(
        ..., 
        description="A concise 3-5 sentence summary summarizing key developments in this section."
    )
    action_items: List[ActionItem] = Field(
        default_factory=list, 
        description="List of specific tasks, decisions, or follow-ups identified in this section."
    )
    key_entities: List[str] = Field(
        default_factory=list, 
        description="Important names, system components, date deadlines, or services mentioned."
    )


class FinalReport(BaseModel):
    """
    The final synthesized operational report consolidating all chunk analyses.
    """
    executive_summary: str = Field(
        ..., 
        description="Comprehensive consolidated executive summary of the entire document."
    )
    consolidated_action_items: List[ActionItem] = Field(
        default_factory=list, 
        description="Deduplicated and structured list of action items across the entire document."
    )
