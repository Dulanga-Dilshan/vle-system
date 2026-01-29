from django.db.models.signals import post_save
from django.dispatch import receiver
from config.models import SystemSettings
from config.config import load_settings



@receiver(post_save,sender=SystemSettings)
def update_cache_on_save(sender, instance, **kwargs):
    #add print
    load_settings()
