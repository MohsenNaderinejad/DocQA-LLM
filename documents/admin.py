from django.contrib import admin
from .models import Document, DocumentChunk


class DocumentChunkInline(admin.TabularInline):
    model = DocumentChunk
    extra = 0  # Don't show blank forms (chunks are auto-generated)
    readonly_fields = ['chunk_index', 'content']  # Can't edit chunks


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    # Show these columns in the list view
    list_display = ['title', 'uploaded_at', 'updated_at']
    
    # Add search box for finding documents
    search_fields = ['title', 'extracted_text']
    
    # These fields are auto-generated, users shouldn't edit them
    readonly_fields = ['extracted_text', 'uploaded_at', 'updated_at']
    
    # Display chunks inline instead of on a separate page
    inlines = [DocumentChunkInline]