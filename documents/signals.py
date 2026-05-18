import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Document, DocumentChunk
from .processing import extract_text_from_docx, split_text_into_chunks


@receiver(post_save, sender=Document)
def process_document(sender, instance, created, **kwargs):
    """
    Automatically process documents when created or file is changed.
    Extracts text and creates searchable chunks.
    """
    if not instance.file:
        return

    # Process new documents immediately
    if created:
        _do_processing(instance)
        return

    # For existing documents, check if the file was changed
    # _loaded_file_name was set in Document.from_db() when document was fetched
    loaded_file_name = getattr(instance, '_loaded_file_name', None)
    new_file_name = instance.file.name if instance.file else None

    # Only reprocess if file was actually changed
    if loaded_file_name != new_file_name:
        _do_processing(instance)

@receiver(post_delete, sender=Document)
def delete_document_file(sender, instance, **kwargs):
    """
    Clean up the physical file when a Document record is deleted.
    Prevents orphaned files from accumulating on the filesystem.
    """
    if instance.file:
        file_path = instance.file.path
        # Check if file exists before deleting to avoid errors
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"### Deleted file: {file_path}")


def _do_processing(instance):
    """Extract text from file, create overlapping chunks."""
    try:
        # Extract text from .docx file
        file_path = instance.file.path
        extracted_text = extract_text_from_docx(file_path)

        # Use .update() to avoid re-triggering the signal
        Document.objects.filter(pk=instance.pk).update(
            extracted_text=extracted_text
        )
        
        # Delete old chunks before creating new ones
        DocumentChunk.objects.filter(document=instance).delete()
        
        # Split into overlapping chunks (500 chars, 50 char overlap)
        chunks = split_text_into_chunks(extracted_text)
        chunk_objects = [
            DocumentChunk(
                document=instance,
                content=chunk,
                chunk_index=i
            )
            for i, chunk in enumerate(chunks)
        ]
        
        # bulk_create is more efficient than looping and saving individually
        DocumentChunk.objects.bulk_create(chunk_objects)
        
        print(f"$$$ Processed '{instance.title}': {len(chunks)} chunks created")
        
    except Exception as e:
        print(f"!!! Error processing '{instance.title}': {e}")