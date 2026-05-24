from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import QAHistory
from .pipeline import ask_question
from .serializers import QAHistorySerializer


@api_view(['POST'])
def ask(request):
    """
    POST /api/ask/
    Body: {"question": "your question here"}
    Returns the generated answer with source documents.
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

        serializer = QAHistorySerializer(qa_entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def history(request):
    """
    GET /api/history/
    Returns the last 20 questions and answers.
    """
    entries = QAHistory.objects.all()[:20]
    serializer = QAHistorySerializer(entries, many=True)
    return Response(serializer.data)