from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import StudentRegistretionRequest


@receiver(post_delete, sender=StudentRegistretionRequest)
def delete_img_file(sender, instance, **kwargs):
    if instance.id_img:
        instance.id_img.delete(save=False)

