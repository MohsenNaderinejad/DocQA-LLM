from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Document, DocumentChunk
from .processing import extract_text_from_docx, split_text_into_chunks


@receiver(post_save, sender=Document)
def process_document(sender, instance, created, **kwargs):
    if not instance.file:
        return

    if created:
        _do_processing(instance)


def _do_processing(instance):
    try:
        file_path = instance.file.path
        extracted_text = extract_text_from_docx(file_path)

        Document.objects.filter(pk=instance.pk).update(
            extracted_text=extracted_text
        )
        
        DocumentChunk.objects.filter(document=instance).delete()
        
        chunks = split_text_into_chunks(extracted_text)
        chunk_objects = [
            DocumentChunk(
                document=instance,
                content=chunk,
                chunk_index=i
            )
            for i, chunk in enumerate(chunks)
        ]
        
        DocumentChunk.objects.bulk_create(chunk_objects)
        
        print(f"$$$ Processed '{instance.title}': {len(chunks)} chunks created")
        
    except Exception as e:
        print(f"!!! Error processing document '{instance.title}': {e}")