from django.contrib import admin
from .models import QAHistory


@admin.register(QAHistory)
class QAHistoryAdmin(admin.ModelAdmin):
    list_display = ['short_question', 'created_at']
    readonly_fields = ['question', 'answer', 'source_documents', 'created_at']

    def short_question(self, obj):
        return obj.question[:80]
    short_question.short_description = 'Question'