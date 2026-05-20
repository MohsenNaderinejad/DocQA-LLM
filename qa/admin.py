from django.contrib import admin
from .models import QAHistory


@admin.register(QAHistory)
class QAHistoryAdmin(admin.ModelAdmin):
    # Show truncated question and creation date in list view
    list_display = ['short_question', 'created_at']
    # Q&A records are read-only (don't edit history)
    readonly_fields = ['question', 'answer', 'source_documents', 'created_at']

    def short_question(self, obj):
        """Display first 80 characters of question in list view."""
        return obj.question[:80]
    short_question.short_description = 'Question'