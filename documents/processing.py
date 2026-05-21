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

def generate_embeddings_for_document(document) -> None:
    """
    After chunks are created, this function converts each chunk's
    text into a vector and saves it to the embedding field.
    """
    from qa.pipeline import embed_text
    from documents.models import DocumentChunk

    chunks = DocumentChunk.objects.filter(
        document=document,
        embedding__isnull=True  # only process chunks that don't have an embedding yet
    )

    print(f"Generating embeddings for {chunks.count()} chunks...")

    for chunk in chunks:
        try:
            # embed_text converts the text string into a list of 384 floats
            chunk.embedding = embed_text(chunk.content)
            chunk.save(update_fields=['embedding'])
        except Exception as e:
            print(f"!!! Chunk {chunk.chunk_index} failed: {e}")

    print(f"$$$ Embeddings done for '{document.title}'")