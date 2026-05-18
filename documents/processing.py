import docx
from typing import List


def extract_text_from_docx(file_path: str) -> str:
    """Extract all paragraphs from a .docx file."""
    doc = docx.Document(file_path)
    
    paragraphs = []
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:  # Skip empty paragraphs
            paragraphs.append(text)
    
    return '\n\n'.join(paragraphs)


def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks for processing."""
    if not text:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # Move forward but keep overlap for context preservation
        start += chunk_size - overlap
    
    return chunks