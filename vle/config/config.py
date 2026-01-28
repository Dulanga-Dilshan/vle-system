import json
import os
from threading import Lock

_lock = Lock()
_settings_chash = {}
_last_update = None

json_path = os.path.join(os.path.dirname(__file__), "json/settings.json")


def load_settings(force:str=):
    with _lock:
        print('loding settings')