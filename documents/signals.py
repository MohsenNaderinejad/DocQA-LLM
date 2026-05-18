from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Document, DocumentChunk
from .processing import extract_text_from_docx, split_text_into_chunks


@receiver(post_save, sender=Document) # Singal for checking if a file was saved or chnaged the contents
def process_document(sender, instance, created, **kwargs):
    if not instance.file:
        return
    
    if created: # Checking creation of DB new record of file
        _do_processing(instance)
        return
    
    try: # Checking if the file was changed to reprocess it or even if it was deleted
        old_instance = Document.objects.get(pk=instance.pk)
        if old_instance.file != instance.file:
            _do_processing(instance)
    except Document.DoesNotExist:
        pass


def _do_processing(instance):
    try:
        file_path = instance.file.path
        extracted_text = extract_text_from_docx(file_path) # Extracting Text from docs file

        Document.objects.filter(pk=instance.pk).update(
            extracted_text=extracted_text
        ) # getting the created document in DB records
        
        DocumentChunk.objects.filter(document=instance).delete() # Deleteing all the chunks related to the saved docs
        
        chunks = split_text_into_chunks(extracted_text) # spliting it in 500 chars parts with 50 char overlaps
        chunk_objects = [
            DocumentChunk(
                document=instance,
                content=chunk,
                chunk_index=i
            )
            for i, chunk in enumerate(chunks)
        ]
        
        DocumentChunk.objects.bulk_create(chunk_objects) # Efficent DB query for saving the docs chunks
        
        print(f"$$$ Processed '{instance.title}': {len(chunks)} chunks created")
        
    except Exception as e:
        print(f"!!! Error processing document '{instance.title}': {e}")