import hashlib
from typing import List, Dict, Any
from src.chunking.base import BaseChunker
from src.models.chunk import DocumentChunk, ChunkMetadata
from src.core.logging import get_logger
from src.core.exceptions import ChunkingError

logger = get_logger(__name__)


class RecursiveCharacterChunker(BaseChunker):
    """
    Splits document text into overlapping chunks using natural boundaries
    (paragraphs, then sentences) while preserving the source page metadata.
    """
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def split_pages(self, pages: List[Dict[str, Any]], source_name: str) -> List[DocumentChunk]:
        if not pages:
            return []

        try:
            # 1. Stitch pages together and build offset mapping to trace page origins
            full_text_parts = []
            offsets = []
            current_offset = 0

            for page in pages:
                text = page["text"]
                page_num = page["page_number"]
                full_text_parts.append(text)
                
                start_off = current_offset
                end_off = current_offset + len(text)
                offsets.append((start_off, end_off, page_num))
                
                # We stitch with "\n\n" separator, which adds 2 characters
                current_offset = end_off + 2

            full_text = "\n\n".join(full_text_parts)
            text_len = len(full_text)

            # 2. Perform chunking using natural boundaries
            chunks = []
            start = 0
            chunk_idx = 0

            while start < text_len:
                end = min(start + self.max_chunk_size, text_len)

                if end < text_len:
                    # Attempt paragraph break first
                    paragraph_break = full_text.rfind("\n\n", start, end)
                    if paragraph_break != -1 and paragraph_break > start:
                        end = paragraph_break + 2
                    else:
                        # Fallback to sentence break
                        sentence_break = full_text.rfind(".", start, end)
                        if sentence_break != -1 and sentence_break > start:
                            end = sentence_break + 1

                chunk_content = full_text[start:end].strip()
                if chunk_content:
                    # 3. Calculate page boundaries for this chunk
                    page_start = None
                    page_end = None

                    # Locate the pages corresponding to start/end character offsets
                    for start_off, end_off, page_num in offsets:
                        if start_off <= start < end_off or (start_off <= start and page_start is None):
                            page_start = page_num
                        if start_off <= end <= end_off or (end >= end_off):
                            page_end = page_num

                    # Set fallback pages in case of boundary mismatches
                    if page_start is None:
                        page_start = pages[0]["page_number"]
                    if page_end is None:
                        page_end = pages[-1]["page_number"]

                    page_end = max(page_start, page_end)

                    # Generate stable deterministic chunk ID
                    content_hash = hashlib.sha256(chunk_content.encode("utf-8")).hexdigest()[:16]
                    chunk_id = f"{source_name}_c{chunk_idx}_{content_hash}"

                    metadata = ChunkMetadata(
                        page_start=page_start,
                        page_end=page_end,
                        section=None,  # Section heading identification could be integrated here
                        source_document=source_name,
                        extra={
                            "chunk_index": chunk_idx,
                            "char_start": start,
                            "char_end": end
                        }
                    )

                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        content=chunk_content,
                        metadata=metadata
                    ))
                    chunk_idx += 1

                # Advance start index accounting for overlap configuration
                start = max(start + 1, end - self.overlap)

            logger.info("Successfully split document into chunks", filename=source_name, total_chunks=len(chunks))
            return chunks

        except Exception as e:
            logger.error("Failed to split document pages into chunks", filename=source_name, error=str(e))
            raise ChunkingError(f"Text chunking failed: {e}") from e
