from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.models.chunk import DocumentChunk


class BaseChunker(ABC):
    """
    Abstract base class defining the contract for all text chunking engines.
    """
    @abstractmethod
    def split_pages(self, pages: List[Dict[str, Any]], source_name: str) -> List[DocumentChunk]:
        """
        Splits a list of structured document pages into semantic/recursive chunks.

        Args:
            pages: List of pages as returned by loader ({page_number: int, text: str}).
            source_name: Name/path of the source file to embed in chunk metadata.

        Returns:
            A list of DocumentChunk objects containing page references.
        """
        pass
