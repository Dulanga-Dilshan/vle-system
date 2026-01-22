from django.contrib.auth import logout
from django.conf import settings
from django.utils import timezone
from datetime import datetime

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
                if inactivity > getattr(settings, 'INACTIVITY_LOGOUT_TIME',900):
                    logout(request)
        return self.get_responce(request)