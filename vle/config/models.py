from django.db import models

class SystemSettings(models.Model):
    settings = models.JSONField(default=dict)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"last update time - {self.last_update}"