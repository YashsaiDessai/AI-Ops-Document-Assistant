from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any


class BaseLoader(ABC):
    """
    Abstract base class defining the contract for all document loaders.
    """
    @abstractmethod
    def load(self, filepath: Path) -> List[Dict[str, Any]]:
        """
        Ingests the document and extracts text page by page.

        Args:
            filepath: Path to the target document.

        Returns:
            A list of pages, where each page is represented as:
            {
                "page_number": int,
                "text": str
            }
        """
        pass
