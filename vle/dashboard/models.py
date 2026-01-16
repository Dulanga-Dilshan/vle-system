from django.db import models
from Users.models import User
# Create your models here.

class Announcement(models.Model):
    title = models.CharField(max_length=50)
    announcement = models.TextField(max_length=500)
    target_audience_rule = models.JSONField(null=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def get_target_display(self)->str:
        if self.target_audience_rule['audience_type'] == 'all':
            return self.target_audience_rule['audience_type']
        
        if self.target_audience_rule['audience_type'] == 'students':
            return f"{self.target_audience_rule['audience_type']} - year:{self.target_audience_rule['group']['year']} - faculty:{self.target_audience_rule['group']['faculty']}"
        
        if self.target_audience_rule['audience_type'] == 'staff':
            return f"{self.target_audience_rule['audience_type']} - staff type:{self.target_audience_rule['group']['type']} - faculty:{self.target_audience_rule['group']['faculty']}"
        
        if self.target_audience_rule['audience_type'] == 'faculty':
            return f"faculty:{self.target_audience_rule['group']['faculty']}"