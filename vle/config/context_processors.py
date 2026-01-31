from config.config import get_setting
from config.settings_schema import SETTINGS_SCHEMA


def vle_settings(request):
    return {
        'settings':{
            key:get_setting(key) for key in SETTINGS_SCHEMA
        }
    }