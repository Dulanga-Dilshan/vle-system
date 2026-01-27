from rest_framework.permissions import BasePermission
from university import models as university_models
from Users.models import User,Staff,Student


class IsSuperUser(BasePermission):
    message = 'no permissions'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
    

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
                    print('1')
                    return False
                
                if user.role == 'student':
                    user = getattr(user,'student',None)
                elif user.role == 'staff':
                    user = getattr(user,'staff',None)
                else:
                    print('2')
                    return False
                
                if user is None:
                    print('3')
                    return False
                
                if staff_admin.faculty_name != user.faculty_name:
                    print('4')
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
