from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class ChunkMetadata(BaseModel):
    """
    Metadata associated with a specific text chunk, preserving physical document structure.
    """
    page_start: int = Field(..., description="The page number where the chunk starts (1-indexed)")
    page_end: int = Field(..., description="The page number where the chunk ends (1-indexed)")
    section: Optional[str] = Field(None, description="The document section title if detected")
    source_document: str = Field(..., description="The filename or path of the source document")
    extra: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Arbitrary additional metadata (e.g. table details, character offsets)"
    )


class DocumentChunk(BaseModel):
    """
    A single chunk of a parsed document ready for LLM extraction or vector database indexation.
    """
    chunk_id: str = Field(..., description="Unique identifier for the chunk (e.g. a hash of the content)")
    content: str = Field(..., description="The text content of the chunk")
    metadata: ChunkMetadata = Field(..., description="Associated metadata for the chunk")
