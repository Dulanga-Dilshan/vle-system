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
        
    def is_targeted(self,user:User)->bool:
        if user is None:
            return False
        
        if user.is_staff:
            return True
        
        if self.target_audience_rule['audience_type'] == 'all':
            return True

        if self.target_audience_rule['audience_type'] == 'students' and user.role == 'student':
            if self.target_audience_rule['group']['year'] == 'all' and self.target_audience_rule['group']['faculty']=='all':
                return True
            
            student = getattr(user,'student',None)
            if not student and not student.batch:
                return False
            
            if self.target_audience_rule['group']['year'] == 'all' and student.faculty_name.name == self.target_audience_rule['group']['faculty']:
                return True
            
            if self.target_audience_rule['group']['faculty']=='all' and str(round(student.batch.progression_year))==self.target_audience_rule['group']['year']:
                return True
            
            if str(round(student.batch.progression_year))==self.target_audience_rule['group']['year']:
                if student.faculty_name.name == self.target_audience_rule['group']['faculty']:
                    return True

        if self.target_audience_rule['audience_type'] == 'staff'  and  user.role == 'staff':
            if self.target_audience_rule['group']['type'] == 'all' and self.target_audience_rule['group']['faculty']=='all':
                return True

            staff = getattr(user,'staff',None)
            if staff is None:
                return False
            
            if self.target_audience_rule['group']['faculty'] == 'all':
                if staff.staff_type == self.target_audience_rule['group']['type']:
                    return True
            
            if self.target_audience_rule['group']['type'] == 'all':
                if staff.faculty_name.name == self.target_audience_rule['group']['faculty']:
                    return True
            
            if staff.faculty_name.name == self.target_audience_rule['group']['faculty']:
                if staff.staff_type == self.target_audience_rule['group']['type']:
                    return True
                
        if self.target_audience_rule['audience_type'] == 'faculty':
            if self.target_audience_rule['group']['faculty'] == 'all':
                return True
            
            if user.role == 'staff':
                staff = getattr(user,'staff',None)
                if self.target_audience_rule['group']['faculty'] == staff.faculty_name.name:
                    return True
            if user.role == 'student':
                student = getattr(user,'student',None)
                if self.target_audience_rule['group']['faculty'] == student.faculty_name.name:
                    return True
            
        return False
            
        
            
class UserAnnouncement(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    announcement = models.ForeignKey(Announcement,on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    removed = models.BooleanField(default=False)
    
    
    class Meta:
        unique_together = ('user','announcement')
    
    def __str__(self):
        return f'{self.announcement.title} - {self.read_at}'


class RecentActivity(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    action = models.CharField(max_length=100)
    at = models.DateTimeField(auto_now_add=True,db_index=True)
    target_content_info = models.JSONField(null=True,default={},blank=True)

    class Meta:
        ordering = ['-at']

    def __str__(self):
        return f"{self.actor} - {self.action} - {self.at }"
    
    


