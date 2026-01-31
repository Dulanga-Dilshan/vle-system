from config.config import sync_setting,_last_update
from config.models import SystemSettings



class SyncSettingsMiddleware:
    def __init__(self,get_responce):
        self.get_responce = get_responce
    
    def __call__(self, request):
        sync_setting()
        return self.get_responce(request)
    
        























'''
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
'''

