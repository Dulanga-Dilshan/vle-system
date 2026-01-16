from rest_framework.permissions import BasePermission


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
                return False
            faculty_id=int(faculty_id)
        else:
            faculty_id = int(view.kwargs.get('id',0))
        
        if staff.faculty_name.id != faculty_id:
            return False
        
        return request.user.is_staff
