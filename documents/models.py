from django.db import models
from pgvector.django import VectorField


class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        # Show newest documents first in admin and queries
        ordering = ['-uploaded_at']

class DocumentChunk(models.Model):
    # Delete chunks when parent document is deleted
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    # The actual text content for this chunk
    content = models.TextField()
    # Order within the document (0, 1, 2, ...)
    chunk_index = models.IntegerField()
    # Vector embedding for this chunk to use pgvector for efficient similarity search
    embedding = VectorField(dimensions=384, null=True, blank=True)

    def __str__(self):
        return f"{self.document.title} — chunk {self.chunk_index}"

    class Meta:
        # Keep chunks in order they were created
        ordering = ['chunk_index']