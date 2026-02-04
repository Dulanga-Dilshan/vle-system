import time
import psutil
import threading


SYSTEM_UP_TIME = None

_latest = {
    "cpu_percent": 0.0,
    "net_down_bps": 0.0,
    "net_up_bps": 0.0,
}

_started = False
_lock = threading.Lock()

#retuns in seconds
def get_system_up_time()->int:
    global SYSTEM_UP_TIME
    if SYSTEM_UP_TIME is None:
        SYSTEM_UP_TIME = time.time()
        return 0
    
    return time.time()-SYSTEM_UP_TIME

def format_time(seconds:int)->str:
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    if days <= 0:
        if hours<=0:
            return f"{int(minutes)}m {int(seconds)}s"
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    return f"{int(days)}d {int(hours)}h {int(minutes)}m"



def memory_usage()->str:
    memory = psutil.virtual_memory()
    return memory.percent



def collector(intervel=1.0):
    global _started
    if _started:
        return

    _started = True

    def run():
        psutil.cpu_percent(interval=None)
        prev_net = psutil.net_io_counters()
        prev_t = time.time()

        while True:
            time.sleep(intervel)
            cpu = psutil.cpu_percent(interval=None)

            now_net = psutil.net_io_counters()
            now_t = time.time()
            dt = max(now_t - prev_t, 1e-6)

            down_bps = (now_net.bytes_recv - prev_net.bytes_recv) / dt
            up_bps   = (now_net.bytes_sent - prev_net.bytes_sent) / dt

            with _lock:
                _latest["cpu_percent"] = cpu
                _latest["net_down_bps"] = down_bps
                _latest["net_up_bps"] = up_bps

            prev_net, prev_t = now_net, now_t
        
    t = threading.Thread(target=run,daemon=True)
    t.start()

def get_net_io_cpu():
    with _lock:
        return _latest.copy()
    

import shutil

#return disk useage presentage
def get_disk_usage()->int:
    disk = shutil.disk_usage("/")
    usage = (disk.used / disk.total) * 100
    return round(usage,2)