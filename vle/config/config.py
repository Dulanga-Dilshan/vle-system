from threading import RLock
from django.db import transaction
from .settings_schema import SETTINGS_SCHEMA

_lock = RLock()
_settings_cache = {}
_last_update = None


def _get_row():
    from .models import SystemSettings
    row, _ = SystemSettings.objects.get_or_create(pk=1, defaults={"settings": {}})
    return row


def load_settings():
    global _settings_cache, _last_update
    row = _get_row()

    with _lock:
        if not _settings_cache:
            _settings_cache = dict(row.settings or {})
            _last_update = row.last_update

    load_schema()


def load_schema():
    global _settings_cache
    changed = False
    with _lock:
        for key, value in SETTINGS_SCHEMA.items():
            if key not in _settings_cache:
                _settings_cache[key] = value['default']
                changed = True
        if changed:
            update_db()


@transaction.atomic
def update_db():
    global _settings_cache, _last_update
    row = _get_row()
    row.settings = _settings_cache
    row.save()
    _last_update = row.last_update


def sync_setting():
    global _settings_cache, _last_update
    from .models import SystemSettings

    last_update = SystemSettings.objects.filter(pk=1).values_list("last_update", flat=True).first()
    if not last_update:
        load_settings()
        return

    if last_update == _last_update:
        return

    row = _get_row()
    with _lock:
        _settings_cache = dict(row.settings or {})
        _last_update = row.last_update


def get_setting(key: str):
    if not _settings_cache:
        load_settings()

    if key in _settings_cache:
        return _settings_cache[key]

    if key in SETTINGS_SCHEMA:
        load_schema()
        return _settings_cache[key]

    raise KeyError(f"System setting '{key}' does not exist")


def update_setting(key: str, value):
    if not _settings_cache:
        load_settings()

    if key not in SETTINGS_SCHEMA:
        raise KeyError(f"System setting '{key}' does not exist")
    


    with _lock:
        _settings_cache[key] = value
        update_db()

def get_all_setting():
    if not _settings_cache:
        load_settings()
    
    all_setting = {}

    for key,value in SETTINGS_SCHEMA.items():
        all_setting[key]=value['default']

    return all_setting

