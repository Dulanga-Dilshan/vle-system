import shutil

#return disk useage presentage
def get_disk_usage()->int:
    disk = shutil.disk_usage("/")
    usage = (disk.used / disk.total) * 100
    return round(usage,2)