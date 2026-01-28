import logging
from typing import List

logger = logging.getLogger(__name__)

def recursive_split(text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Splits text into chunks respecting natural boundries (paragraphs, then sentences).

    Args:
        text: The full document texxt.
        max_chunk_size: MAximum chracters per chunk.
        overlap: Number of chracters to overlap between chunks to preserve context at edges 
        """
    if not text:
        return[]

    chunks = []
    start = 0 
    text_len = len(text)

    while start < text_len:
        end =min(start + max_chunk_size, text_len)
        
        if end < text_len:
            paragraph_break = text.rfind("\n\n", start, end)

            if paragraph_break ! = -1 and paragraph_break > start:
                end = paragraph_break + 2
                
            else:
                sentence_break = text.rfind(".", start, end)
                if sentence_break ! = -1 and sentence_break > start:
                    end = sentence_break + 1 

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = max(start + 1 , end - overlap)
    
    logger.info(f"Split document into {len(chunks)} chunks.")
    return chunks

