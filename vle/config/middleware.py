from config.config import sync_setting
import time
import threading
from config.metrics import get_system_up_time


class SyncSettingsMiddleware:
    def __init__(self,get_responce):
        self.get_responce = get_responce
    
    def __call__(self, request):
        sync_setting()
        return self.get_responce(request)
    
class SystemUptimeMiddleware:
    def __init__(self,get_responce):
        self.get_responce = get_responce
    
    def __call__(self, request):
        get_system_up_time()
        return self.get_responce(request)
    
        

_lock = threading.Lock()
_count = 0
_total_ms = 0.0

def get_avg_response_ms() -> float:
    with _lock:
        return (_total_ms / _count) if _count else 0.0

def get_request_count() -> int:
    with _lock:
        return _count

class AvgResponseTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/static/") or request.path.startswith("/media/"):
            return self.get_response(request)
            
        global _count, _total_ms
        start = time.perf_counter()
        response = self.get_response(request)
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        with _lock:
            _count += 1
            _total_ms += elapsed_ms

        return response