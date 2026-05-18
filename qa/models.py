from django.db import models
from documents.models import Document


class QAHistory(models.Model):
    question = models.TextField()
    answer = models.TextField()
    source_documents = models.ManyToManyField(
        Document,
        blank=True,
        related_name='qa_history'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.question[:60]}..."

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'QA History'
        verbose_name_plural = 'QA History'