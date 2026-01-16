from django.contrib import admin
from . import models


# Register your models here.

admin.site.register(models.University)
admin.site.register(models.Faculty)
admin.site.register(models.Department)

admin.site.register(models.Course)
admin.site.register(models.Batch)
admin.site.register(models.Subject)
admin.site.register(models.Semester)
admin.site.register(models.BatchSubject)