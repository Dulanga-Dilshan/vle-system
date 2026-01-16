from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,Staff,Student,StudentRegistretionRequest,StaffRegistretionRequest

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username','email','role','is_staff','is_active','last_activity')
    list_filter = ('role','is_staff')
    
    fieldsets=UserAdmin.fieldsets+(
        ('role',{'fields':('role',)}),
    )

    add_fieldsets=UserAdmin.add_fieldsets+(
       (None,{'fields':('role',)}), 
    )    

admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(StudentRegistretionRequest)
admin.site.register(StaffRegistretionRequest)