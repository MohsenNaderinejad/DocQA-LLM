from django.contrib import admin
from .models import Document, DocumentChunk


class DocumentChunkInline(admin.TabularInline):
    model = DocumentChunk
    extra = 0
    readonly_fields = ['chunk_index', 'content']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_at', 'updated_at']
    search_fields = ['title', 'extracted_text']
    readonly_fields = ['extracted_text', 'uploaded_at', 'updated_at']
    inlines = [DocumentChunkInline]