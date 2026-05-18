import docx
from typing import List


def extract_text_from_docx(file_path: str) -> str:
    """
    Opens a .docx file and extracts all paragraph text.
    Returns the full text as a single string.
    """
    doc = docx.Document(file_path)
    
    paragraphs = []
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:  # skip empty paragraphs
            paragraphs.append(text)
    
    return '\n\n'.join(paragraphs)


def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Splits a long text into overlapping chunks.
    
    chunk_size: how many characters per chunk
    overlap: how many characters to repeat between consecutive chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # move forward but keep some overlap
    
    return chunks