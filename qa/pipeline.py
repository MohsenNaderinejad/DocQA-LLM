import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from documents.models import DocumentChunk


def get_llm():
    """
    Initialize and return the configured LLM client.
    Centralized here so changing the model only requires .env update.
    """
    return ChatOpenAI(
        openai_api_key=os.getenv('OPENROUTER_API_KEY'),
        openai_api_base="https://openrouter.ai/api/v1",
        model_name=os.getenv('OPENROUTER_MODEL', 'nvidia/nemotron-3-super-120b-a12b:free'),
        temperature=0.1,  # Low temperature = more factual, less creative
        max_tokens=1000,  # Limit response length
        # OpenRouter tracking headers
        default_headers={
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "DocQA System"
        }
    )


def find_relevant_chunks(question: str, top_k: int = 4) -> list:
    """
    Find the most relevant document chunks for a question using keyword matching.
    
    Args:
        question: User's question
        top_k: Number of chunks to return (default 4)
    
    Returns:
        List of DocumentChunk objects sorted by relevance
    
    Note: This is a simple keyword search. Will upgrade to vector search after pgvector setup.
    """
    # Extract meaningful words from question (filter out short/common words)
    question_words = [
        word.lower() 
        for word in question.split() 
        if len(word) > 3
    ]
    
    # If no valid words found, return any chunks
    if not question_words:
        return list(DocumentChunk.objects.all()[:top_k])
    
    # Score each chunk by counting matches with question words
    chunks = DocumentChunk.objects.all()
    scored = []
    
    for chunk in chunks:
        content_lower = chunk.content.lower()
        # Count how many question words appear in this chunk
        score = sum(1 for word in question_words if word in content_lower)
        if score > 0:
            scored.append((score, chunk))
    
    # Sort by score (highest first) and return top_k
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


def build_prompt_context(chunks: list) -> str:
    """
    Format document chunks into readable context for the LLM.
    
    Args:
        chunks: List of DocumentChunk objects
    
    Returns:
        Formatted context string with document titles and chunk indices
    """
    if not chunks:
        return "No relevant documents found."
    
    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"[Document: {chunk.document.title}, Chunk {chunk.chunk_index}]\n"
            f"{chunk.content}"
        )
    
    # Separate chunks with visual delimiter
    return "\n\n---\n\n".join(context_parts)


def ask_question(question: str) -> dict:
    """
    Main Q&A pipeline: search for relevant chunks, build context, query LLM.
    
    Args:
        question: User's question as a string
    
    Returns:
        Dictionary with:
        - answer: LLM's response
        - source_documents: List of Document objects used
        - chunks_used: Number of chunks retrieved
    """
    # Step 1: Find relevant chunks using keyword search
    relevant_chunks = find_relevant_chunks(question)
    
    # Step 2: Format chunks into context string
    context = build_prompt_context(relevant_chunks)
    
    # Step 3: Initialize LLM client
    llm = get_llm()
    
    # Step 4: Create system + user messages
    messages = [
        SystemMessage(
            content="""You are a helpful assistant that answers questions based strictly on 
the provided document context. If the answer is not in the context, say so clearly. 
Do not make up information."""
        ),
        HumanMessage(
            content=f"""Context from documents:

{context}

Question: {question}

Answer based only on the context above:"""
        )
    ]
    
    # Step 5: Call LLM and get response
    response = llm.invoke(messages)
    answer = response.content
    
    # Step 6: Extract source documents (remove duplicates using set)
    source_docs = list({chunk.document for chunk in relevant_chunks})
    
    return {
        'answer': answer,
        'source_documents': source_docs,
        'chunks_used': len(relevant_chunks)
    }