from django.db.models.signals import post_delete,pre_save
from django.dispatch import receiver
from .models import LectureMaterials


@receiver(post_delete, sender=LectureMaterials)
def delete_lecture_materials_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)


@receiver(pre_save,sender=LectureMaterials)
def delete_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return
    
    try:
        old_file = LectureMaterials.objects.get(pk=instance.pk).file
    except LectureMaterials.DoesNotExist:
        return

    new_file = instance.file
    if old_file and old_file != new_file:
        old_file.delete(save=False)
    

