from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'extracted_text', 'uploaded_at', 'updated_at', 'chunk_count']
        read_only_fields = ['extracted_text', 'uploaded_at', 'updated_at']

    def get_chunk_count(self, obj):
        """Returns how many chunks this document was split into."""
        return obj.chunks.count()