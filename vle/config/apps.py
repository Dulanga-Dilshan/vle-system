import os
from django.apps import AppConfig
from config.config import load_settings


class ConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'config'
