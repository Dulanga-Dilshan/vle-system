from threading import Lock
from .settings_schema import SETTINGS_SCHEMA
from django.db import transaction
from datetime import datetime

_lock = Lock()
_settings_chash = {}

def load_settings()->None:
    global _settings_chash
    from .models import SystemSettings
    with _lock:
        system_settings = SystemSettings.objects.first()
        if not system_settings:
            load_schema(db_save=True)
            system_settings = SystemSettings.objects.first()

        if not _settings_chash:
            _settings_chash = system_settings.settings


def load_schema(db_save = False):
    global _settings_chash
    with _lock:
        for key,value in SETTINGS_SCHEMA.items():
            _settings_chash[key] = value
        
        if db_save:
            update_db()



@transaction.atomic
def update_db():
    global _settings_chash
    from config.models import SystemSettings
    system_settings = SystemSettings.objects.first()
    if system_settings is None:
        SystemSettings.objects.create(settings= _settings_chash,pk=1)
    
    else:
        system_settings.settings = _settings_chash
        try:
            system_settings.save()
        except Exception as e:
            print(str(e))