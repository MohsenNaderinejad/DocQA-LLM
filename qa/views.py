from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import QAHistory
from .pipeline import ask_question


@api_view(['POST'])
def ask(request):
    """
    POST /api/ask/
    Body: {"question": "What is the contract duration?"}
    Returns: {"answer": "...", "question": "...", "id": 1}
    """
    question = request.data.get('question', '').strip()
    
    if not question:
        return Response(
            {'error': 'Question cannot be empty'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = ask_question(question)
        
        # Save to history
        qa_entry = QAHistory.objects.create(
            question=question,
            answer=result['answer']
        )
        qa_entry.source_documents.set(result['source_documents'])
        qa_entry.save()
        
        return Response({
            'id': qa_entry.id,
            'question': question,
            'answer': result['answer'],
            'sources': [doc.title for doc in result['source_documents']],
            'chunks_used': result['chunks_used']
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def history(request):
    """
    GET /api/history/
    Returns list of all past questions and answers.
    """
    entries = QAHistory.objects.all()[:20]  # last 20
    data = [
        {
            'id': e.id,
            'question': e.question,
            'answer': e.answer,
            'created_at': e.created_at,
            'sources': [doc.title for doc in e.source_documents.all()]
        }
        for e in entries
    ]
    return Response(data)