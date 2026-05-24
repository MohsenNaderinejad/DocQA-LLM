from rest_framework import serializers
from .models import QAHistory


class QAHistorySerializer(serializers.ModelSerializer):
    sources = serializers.SerializerMethodField()

    class Meta:
        model = QAHistory
        fields = ['id', 'question', 'answer', 'sources', 'created_at']
        read_only_fields = ['answer', 'created_at']

    def get_sources(self, obj):
        return [doc.title for doc in obj.source_documents.all()]