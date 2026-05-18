from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Document, DocumentChunk
from .processing import extract_text_from_docx, split_text_into_chunks


@receiver(post_save, sender=Document)
def process_document(sender, instance, created, **kwargs):
    """Trigger document processing on creation or file change."""
    if not instance.file:
        return
    
    # Process new documents
    if created:
        _do_processing(instance)
        return
    
    # Process if file was changed
    try:
        old_instance = Document.objects.get(pk=instance.pk)
        if old_instance.file != instance.file:
            _do_processing(instance)
    except Document.DoesNotExist:
        pass


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