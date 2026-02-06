from dashboard.models import RecentActivity
from Users.models import User
from django.db import transaction




@transaction.atomic
def log_activity(actor:User,action:str,content_info:dict=None):
    new_activity = RecentActivity(
        actor=actor,
        action=action
    )

    if content_info and type(content_info)==dict:
        new_activity.target_content_info = content_info
    
    new_activity.save()


