from threading import RLock
from django.db import transaction
from .settings_schema import SETTINGS_SCHEMA, TYPE_MAP
from rest_framework.exceptions import ValidationError
from validators import url,email


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
    
    validate_setting(key=key,value=value)

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


def validate_setting(key:str,value):
    setting = SETTINGS_SCHEMA[key]

    if 'type' in setting:
        if setting['type'] not in TYPE_MAP:
            raise ValidationError(f"Invalide type for value:{value}. expected type:{setting['type']}")
        
        if type(value) != TYPE_MAP[setting['type']]:
            raise ValidationError(f"Invalide type for value:{value}. expected type:{setting['type']}, received {type(value)}")
        
    if 'rules' in setting:
        if 'strip' in setting['rules'] and setting['rules']['strip']==True:
                value = value.strip()

        for rule_key,rue_value in setting['rules'].items():

            if rule_key == 'allow_empty' and value=="":
                return value

            if rule_key == 'min_length':
                if len(value)<rue_value:
                    raise ValidationError(f"Value is too short for key:{key}. Minimum length is {rue_value} characters, received {len(value)}.")
            
            if rule_key == 'max_length':
                if len(value)>rue_value:
                    raise ValidationError(f"Value is too large for key:{key}. Max length is {rue_value} characters, received {len(value)}.")
            
            if rule_key == 'format':
                if rue_value == 'url':
                    if not url(value):
                            raise ValidationError("Invalid URL format. eg:- https://example.com")
                
                if rue_value == 'csv_extensions':
                    extensions = value.split(',')
                    for extnsion in extensions:
                        if extnsion[0] != '.':
                            raise ValidationError(
                                f"extensions in incorrect format. expected {SETTINGS_SCHEMA['ALLOWED_FILE_EXTENSIONS']['default']}."
                            )
                
                if rue_value == 'email':
                    if not email(value):
                        raise ValidationError("Invalid Email format. eg:- user@example.com")
                    


            if rule_key == 'min':
                if value<rue_value:
                    raise ValidationError(f"Value is too short for key:{key}. Minimum is {rue_value} , received {value}.")

            if rule_key == 'max':
                if value>rue_value:
                    raise ValidationError(f"Value is too big for key:{key}. max is {rue_value} , received {value}.")
            
            if rule_key == 'item_type':
                for item in value:
                    if type(item) != TYPE_MAP[rue_value]:
                        raise ValidationError(f"Invalid item type: all items must be same type")
            
            if rule_key == 'choices':
                for item in value:
                    if item not in rue_value:
                        raise ValidationError(
                            f"Invalid item in list: {item}. "
                            f"Valid items are: {', '.join(map(str, rue_value))}"
                        )
            
            if rule_key == "unique_items":
                items = []
                for item in value:
                    if item not in items:
                        items.append(item)
                    else:
                        raise ValidationError(f"values must be unique. got repeted item {item}")
            
            if rule_key == 'min_items':
                if len(value)<rue_value:
                    raise ValidationError(f"value count cant be less than {rue_value}. got {len(value)}")
            
            if rule_key == 'max_items':
                if len(value)>rue_value:
                    raise ValidationError(f"value count cant be greter than {rue_value}. got {len(value)}")
    return value

                
            



                
            

                
            
            

            