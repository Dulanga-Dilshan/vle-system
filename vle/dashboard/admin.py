from django.contrib import admin
from .models import Announcement,UserAnnouncement

# Register your models here.

admin.site.register(Announcement)
admin.site.register(UserAnnouncement)