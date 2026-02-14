from rest_framework.permissions import BasePermission
from university import models as university_models
from Users.models import User,Staff,Student


class IsSuperUser(BasePermission):
    message = 'no permissions'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
    
class IsAdmin(BasePermission):
    message = 'no permissions'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

    
class IsFacultyAdminstrator(BasePermission):
    message = 'unotherized'

    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True

        staff = getattr(request.user,'staff',None)
        
        if not staff:
            return False
        
        if request.method == "POST":
            faculty_id = request.data.get('faculty')
            if not faculty_id:
                users = request.data['users']
                faculty_id = users[0]['faculty_id']
                if not faculty_id:
                    return False
                for user in users:
                    if user['faculty_id'] != faculty_id:
                        return False
                
        
            faculty_id=int(faculty_id)
        else:
            faculty_id = int(view.kwargs.get('id',0))
        
        if staff.faculty_name.id != faculty_id:
            return False
        
        return request.user.is_staff


class IsBatchAdminstrator(BasePermission):
    message = 'unauthorized'

    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        
        staff = getattr(request.user,'staff',None)
        
        if not staff:
            return False
        
        if request.method == 'POST':
            course_id = request.data.get('course')
            if not course_id:
                return False
            course_id=int(course_id)
            course = university_models.Course.objects.filter(id=course_id).first()
            if not course:
                return False
            
            if course.department.faculty.id != staff.faculty_name.id:
                return False

        else:
            batch_id = int(view.kwargs.get('id',0))
            batch = university_models.Batch.objects.filter(id=batch_id).first()
            if not batch:
                return False
            
            if batch.course.department.faculty.id != staff.faculty_name.id:
                return False
        
        return request.user.is_staff


class IsFacultyAdminUserState(BasePermission):
    message = 'unouthorized'

    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True

        if request.method == 'POST' or request.method == 'DELETE':
            user_id = request.data.get('user_id')
            staff_admin = Staff.objects.filter(username=request.user).first()
            if user_id != None:
                user = User.objects.filter(id=user_id).first()
                if user is None:
                    return False
                
                if user.role == 'student':
                    user = getattr(user,'student',None)
                elif user.role == 'staff':
                    user = getattr(user,'staff',None)
                else:
                    return False
                
                if user is None:
                    return False
                
                if staff_admin.faculty_name != user.faculty_name:
                    return False
            
            else:
                user_ids = request.data.get('user_ids')
                if user_ids is None or len(user_ids)<1:
                    return False
                
                users = User.objects.filter(id__in=user_ids)
                if users is None or len(users)<1:
                    return False
                for user in users:
                    if user is None:
                        return False
                    
                    if user.role == 'student':
                        faculty_member = getattr(user,'student',None)
                    elif user.role == 'staff':
                        faculty_member = getattr(user,'staff',None)
                    else:
                        return False
                    
                    if staff_admin.faculty_name != faculty_member.faculty_name:
                        return False


            return request.user.is_staff
        
        return False

class IsAuthenticated(BasePermission):
    message = 'login requered'

    def has_permission(self, request, view):
        if request.user:
            return request.user.is_authenticated
        
        return False
    
class IsValiedAssignment(BasePermission):
    message = 'Invalied Assignment'

    def has_permission(self, request, view):
        batch = university_models.Batch.objects.filter(id=request.data['batch_id']).first()
        subject = university_models.Subject.objects.filter(id=request.data['subject_id']).first()
        staff = Staff.objects.filter(id=request.data['teacher_id']).exclude(staff_type='support').first()

        if batch is None or subject is None:
            return False

        if batch.course.department != subject.department:
            return False
        
        if request.user and request.user.is_superuser:
            return True
        
        if request.user.is_staff == 0:
            return False
        
        if staff is not None:
            faculty_member = getattr(request.user,'staff',None)
            if faculty_member.faculty_name != subject.department.faculty:
                return False
        
        return True


class IsFacultyAdminAdvanceBatch(BasePermission):
    message = 'unouthorized'

    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        
        try:
            batch_id = int(view.kwargs.get('batch_id',0))
        except Exception:
            return False
        
        batch = university_models.Batch.objects.filter(id=batch_id).first()
        
        if request.user.is_staff == 1:
            faculty_member = getattr(request.user,'staff',None)
            if faculty_member.faculty_name == batch.course.department.faculty:
                return True
        
        return False
        
