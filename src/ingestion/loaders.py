from pathlib import Path
from typing import List, Dict, Any
import pdfplumber

from src.ingestion.base import BaseLoader
from src.core.exceptions import IngestionError
from src.core.logging import get_logger

logger = get_logger(__name__)


class PDFLoader(BaseLoader):
    """
    Ingestion engine for PDF documents using pdfplumber.
    """
    def load(self, filepath: Path) -> List[Dict[str, Any]]:
        pages = []
        try:
            with pdfplumber.open(filepath) as pdf:
                total_pages = len(pdf.pages)
                logger.info("Opening PDF file for text extraction", filename=filepath.name, total_pages=total_pages)

                for i, page in enumerate(pdf.pages):
                    text = page.extract_text(layout=True)
                    if text and text.strip():
                        pages.append({
                            "page_number": i + 1,
                            "text": text
                        })
                    else:
                        logger.warning("PDF page skipped: empty or image-only page", page_number=i + 1)
        except Exception as e:
            logger.error("Failed to extract text from PDF document", filename=filepath.name, error=str(e))
            raise IngestionError(f"PDF extraction failure: {e}") from e

        return pages


class TXTLoader(BaseLoader):
    """
    Ingestion engine for plain text files with encoding fallback mechanisms.
    """
    def load(self, filepath: Path) -> List[Dict[str, Any]]:
        logger.info("Opening TXT file for ingestion", filename=filepath.name)
        try:
            text = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("UTF-8 decoding failed, trying Latin-1 encoding fallback", filename=filepath.name)
            try:
                text = filepath.read_text(encoding="latin-1")
            except Exception as e:
                logger.error("All text decoding configurations failed", filename=filepath.name, error=str(e))
                raise IngestionError(f"TXT extraction failure: {e}") from e
        except Exception as e:
            logger.error("Failed to read text file content", filename=filepath.name, error=str(e))
            raise IngestionError(f"TXT extraction failure: {e}") from e

        return [{"page_number": 1, "text": text}]


def get_loader(filepath: Path) -> BaseLoader:
    """
    Factory function resolving the appropriate loader based on the file suffix.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Input file not found at path: {filepath}")

    suffix = filepath.suffix.lower()
    if suffix == ".pdf":
        return PDFLoader()
    elif suffix == ".txt":
        return TXTLoader()
    else:
        raise IngestionError(f"Unsupported file format: '{suffix}'. Supported formats are: .pdf, .txt")
