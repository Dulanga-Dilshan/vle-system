from .models import User, Student, Staff,StudentRegistretionRequest, StaffRegistretionRequest
from university import models as univercity_models
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest

def approve_register_request(ids,role):
    if role == 'student':
        for id in ids:
            std_request=StudentRegistretionRequest.objects.get(id=id)
            user = User(
                username = std_request.username,
                email = std_request.email,
                first_name = std_request.first_name,
                last_name = std_request.last_name,
                role = 'student',
                password = std_request.passwd_hash
            )

            try:
                user.save()
            except:
                return False

            student = Student(
                name = f"{std_request.first_name} {std_request.last_name}" ,
                username = User.objects.get(username=std_request.username),
                faculty_name = std_request.faculty_name,
                department_name = std_request.department_name
            )

            try:
                student.save()
                std_request.delete()
            except Exception as e:
                return False
        else:
            return True
    
    elif role == 'staff':
        for id in ids:
            request = StaffRegistretionRequest.objects.get(id=id)
            name = request.fullname.split(' ')
            if len(name) > 1:
                fname, lname = name[0] , name[1] 
            else:
                fname = request.fullname
                lname = ''
            
            user = User(
                username = request.username,
                email = request.email,
                first_name = fname,
                last_name = lname,
                role = 'staff',
                password = request.passwd_hash
            )

            if request.staff_type == 'admin':
                user.is_staff = 1

            try:
                user.save()
            except:
                return False

            staff = Staff(
                name = request.fullname ,
                faculty_name = request.faculty_name,
                department_name = request.department_name,
                username = User.objects.get(username=request.username),
                staff_type = request.staff_type
            )

            try:
                staff.save()
                request.delete()
            
            except Exception as e:
                return False
            
        else:
            return True

    else:
        raise ValueError("invalid user type")



def delete_ragistration_requests(ids, role):
    if role=='student':
        for id in ids:
            request=get_object_or_404(StudentRegistretionRequest,id=id)
            if request:
                request.delete()

    
    elif role=='staff':
        for id in ids:
            request = get_object_or_404(StaffRegistretionRequest,id=id)
            if request:
                request.delete()
    else:
        raise ValueError("invalid user type")
    

def delete_user(usr_id:int)->None:
    user=get_object_or_404(User,id=usr_id)
    if user:
        user.delete()


def rest_passwd(user_id:int)->None:
    user=get_object_or_404(User,id=user_id)
    if user:
        user.set_password(getattr(settings, 'DEFAULT_USER_PASSWORD'))
        user.save()

def set_user_state(user_id:int,action:str='suspend')->None:
    user=get_object_or_404(User,id=user_id)
    if user:
        if action=='suspend':
            user.is_active = 0
        elif action=='activate':
            user.is_active= 1
        user.save()

    
def check_permission_administater(user:User)->bool:
    if user.is_staff:
        return True
    
    return False

def get_request_count()->int:
    students = StudentRegistretionRequest.objects.count()
    staff = StaffRegistretionRequest.objects.count()

    return staff+students

def max_user_count()->int:
    return getattr(settings,'MAX_USER_COUNT')

def user_count(faculty_id:int=None,department_id:int=None,admins:bool=True)->int:
    if faculty_id:
        count = Student.objects.filter(faculty_name=faculty_id).count()
        count += Staff.objects.filter(faculty_name=faculty_id).count()
        return count
    
    if department_id:
        count = Student.objects.filter(department_name=department_id).count()
        count += Staff.objects.filter(department_name=department_id).count()

    if not admins:
        return User.objects.exclude(role='admin').count()

    return User.objects.count()


def create_user_student(user_data:dict,student_data:dict)->bool:
    if len(user_data['full_name'].split(' ')) > 1:
        first_name = user_data['full_name'].split(' ')[0]
        last_name = user_data['full_name'].split(' ')[1]
    else:
        first_name = user_data['full_name']
        last_name = ''

    userAcc = User(
        username = user_data['username'],
        email = user_data['email'],
        first_name = first_name,
        last_name = last_name,
        role = 'student'
    )

    try:
        userAcc.save()
    except Exception as e:
        print(e)
        return e
    
    studentAcc = Student(
        name = student_data['name'],
        faculty_name = univercity_models.Faculty.objects.get(id=student_data['faculty_id']),
        department_name = univercity_models.Department.objects.get(id=student_data['department_id']),
        batch = univercity_models.Batch.objects.get(id=student_data['batch_id']),
        username = userAcc
    )

    try:
        studentAcc.save()
    except Exception as e:
        print(e)
        return e
    
    return True



