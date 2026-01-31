from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SystemSettings
from .config import sync_setting

@receiver(post_save, sender=SystemSettings)
def sync_system_settings(sender, instance, **kwargs):
    sync_setting()  
