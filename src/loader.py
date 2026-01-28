import logging
from pathlib import Path
from typing import Union
import pdfplumber

logger = logging.getLogger(__name__)

def load_pdf(filepath: Path) -> str:
    """
    Extracts text from a PDF while preserving the physical layout .

    Uses pdfplumber to detect visual lines and columns, ensuring that 
    tables and sidebars are extracted in a readable order, rather than 
    a jumbled character stream.
    """
    full_text = []
    try:
        with pdfplumber.open(filepath) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"Processing PDF with {total_pages} pages ...")

            for i, page in enumerate(pdf.pages):
                text = page.extract_text(layout=True)

            if text:
                full_text.append(text)
            else:
                logger.warning(f"Page {i+1} is empty or contains only images. ")

    except Exception as e:
        logger.error(f"Failed to parse PDF {filepath}: {e}")
        raise
    return "\n\n".join(full_text)

def load_txt(filepath: Path) -> str:
    """
    Simple loader for plain text files.
    """
    try:
        return filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning("UTF-8 failed, trying latin-1 fallback.")
        return filepath.read_text(encoding = "latin-1")

def load_document(filepath: Union[str, Path]) -> str:
    """
    Main entry point. Determines file type and dispatches to the correct loader.
    """
    path_obj = Path(filepath)

    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")
    
    extension = path_obj.suffix.lower()

    if extension == ".pdf":
        return load_pdf(path_obj)
    elif extension == ".txt":
        return load_txt(path_obj)
    else:
        raise ValueError(f"Unsupported file format: {extension}")
