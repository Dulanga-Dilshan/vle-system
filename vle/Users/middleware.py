from django.contrib.auth import logout
from django.utils import timezone
from config.config import get_setting
from django.shortcuts import render

class UpdateLastActivityMiddleware:
    def __init__(self,get_responce):
        self.get_responce=get_responce

    def __call__(self, request):
        if request.user.is_authenticated:
            request.user.last_activity = timezone.now()
            request.user.save(update_fields=['last_activity'])
        return self.get_responce(request)
    
    
class AutoLogoutMiddleware:
    def __init__(self,get_responce):
        self.get_responce=get_responce
    
    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity=request.user.last_activity
            if last_activity:
                inactivity =  (timezone.now() -  last_activity).total_seconds()
                if inactivity > get_setting('INACTIVITY_LOGOUT_TIME'):
                    logout(request)
        return self.get_responce(request)
    

class CheckMaintainModeMiddleware:
    def __init__(self,get_responce):
        self.get_responce= get_responce
    
    def __call__(self, request):
        if request.user.is_authenticated:
            if get_setting('MAINTENANCE_MODE'):
                if request.user.role not in get_setting("MAINTENANCE_ALLOWED_ROLES"):
                    logout(request)
                    return render(request,"Users/login.html",{'error':"Not Allowed During MAINTENANCE_MODE"})

        return self.get_responce(request)