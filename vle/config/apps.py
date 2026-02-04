from django.apps import AppConfig
import time
class ConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'config'

    def ready(self):
        import config.signals
        from config.metrics import SYSTEM_UP_TIME
        SYSTEM_UP_TIME = time.time()


