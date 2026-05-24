from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import Document
from .serializers import DocumentSerializer


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
def document_list(request):
    """
    GET  /api/documents/ — returns list of all documents
    POST /api/documents/ — uploads a new document
    """

    if request.method == 'GET':
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True, context={'request': request})
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = DocumentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
def document_detail(request, pk):
    """
    GET    /api/documents/<id>/ — returns a single document
    DELETE /api/documents/<id>/ — deletes a document
    """
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response(
            {'error': 'Document not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = DocumentSerializer(document, context={'request': request})
        return Response(serializer.data)

    if request.method == 'DELETE':
        title = document.title
        document.delete()
        return Response(
            {'message': f"Document '{title}' deleted successfully"},
            status=status.HTTP_200_OK
        )