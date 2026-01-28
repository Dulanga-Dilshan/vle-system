from .models import User, Student, Staff,StudentRegistretionRequest, StaffRegistretionRequest
from university import models as univercity_models
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from rest_framework.exceptions import ValidationError, NotFound
from django.db import transaction
from django.core.validators import validate_email

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
    

def delete_user(usr_id:int)->bool:
    user=User.objects.filter(id=usr_id).first()
    if user:
        user.delete()
        return True
    return False



def rest_passwd(user_id:int)->bool:
    user=User.objects.filter(id=user_id).first()
    if user:
        user.set_password(getattr(settings, 'DEFAULT_USER_PASSWORD'))
        user.save(update_fields=["password"])
        return True
    return False



def set_user_state(user_id:int,action:str='suspend')->bool:
    user=get_object_or_404(User,id=user_id)
    if user:
        if action=='suspend':
            user.is_active = 0
        elif action=='activate':
            user.is_active= 1
        else:
            return False
        try:
            user.save()
        except Exception as e:
            return False
        return True

    
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

    userAcc.set_password(getattr(settings, 'DEFAULT_USER_PASSWORD'))

    try:
        userAcc.save()
    except Exception as e:
        print(e)
        return e
    
    if not student_data['batch_id']:
        batch = None
    else:
        batch = univercity_models.Batch.objects.get(id=student_data['batch_id'])
        
    
    studentAcc = Student(
        name = student_data['name'],
        faculty_name = univercity_models.Faculty.objects.get(id=student_data['faculty_id']),
        department_name = univercity_models.Department.objects.get(id=student_data['department_id']),
        batch = batch,
        username = userAcc
    )

    try:
        studentAcc.save()
    except Exception as e:
        print(e)
        return e
    
    return True


def create_user_staff(user_data:dict,staff_data:dict)->bool:
    if len(user_data['full_name'].split(' ')) > 1:
        first_name = user_data['full_name'].split(' ')[0]
        last_name = "".join(user_data['full_name'].split(' ')[1:])
    else:
        first_name = user_data['full_name']
        last_name = ''

    is_staff = 0
    if staff_data['staff_type'] == 'admin':
        is_staff = 1

    userAcc = User(
        username = user_data['username'],
        email = user_data['email'],
        first_name = first_name,
        last_name = last_name,
        role = 'staff',
        is_staff = is_staff
    )

    userAcc.set_password(getattr(settings, 'DEFAULT_USER_PASSWORD'))

    try:
        userAcc.save()
    except Exception as e:
        print(e)
        return e

    staffAcc = Staff(
        name = staff_data['name'],
        username = userAcc,
        staff_type = staff_data['staff_type'],
        faculty_name = univercity_models.Faculty.objects.get(id=staff_data['faculty_id']),
        department_name = univercity_models.Department.objects.get(id=staff_data['department_id']),
    )

    try:
        staffAcc.save()
    except Exception as e:
        print(e)
        return e
    
    return True

@transaction.atomic
def update_user(data:dict):

    #validations
    if not User.objects.filter(id=data['user_id']).exists():
            raise NotFound(
                "user dosn't exsists!"
            )
    if 'email' in data:
        validate_email(data['email'])
    
    if 'name' in data and data['name'] is not None:
        if len(data['name'].strip()) <1:
            raise ValidationError(
                "invalid name."
            )
    if 'faculty_id' in data:
        if 'faculty_id' in data['faculty_id'] is not None:
            if data['department_id'] is None:
                raise ValidationError(
                    'wrong faculty and department combo'
                )
            
            try:
                department = univercity_models.Department.objects.get(id=data['department_id'])
            except univercity_models.Department.DoesNotExist:
                raise ValidationError('Invalid department id')

            if department.faculty.id != data['faculty_id']:
                raise ValidationError(
                    'wrong faculty and department combo'
                )
    
    #save
    user = User.objects.get(id=data['user_id'])

    if 'email' in data:
        if data['email'] != user.email:
            user.email = data['email']

    try:
        sub_user = Student.objects.get(username=user) if data['user_type'] == 'student' else Staff.objects.get(username=user)
    except (Student.DoesNotExist,Staff.DoesNotExist):
        raise ValidationError(
            "user dosn't exsists!"
        )
    
    if 'name' in data:
        if sub_user.name != data['name'] and data['name'] is not None:
            sub_user.name = data['name']
            full_name = data['name'].strip().split(' ')
            if len(full_name)>1:
                user.first_name = full_name[0]
                user.last_name = " ".join(full_name[1:])

            else:
                user.first_name = full_name[0]
                user.last_name = ''
    
    if 'faculty_id' in data and data['faculty_id'] is not None:
        if sub_user.faculty_name.id != data['faculty_id'] and data['faculty_id'] is not None:
                sub_user.faculty_name = univercity_models.Faculty.objects.get(id=data['faculty_id'])

        if sub_user.department_name.id != data['department_id'] and data['department_id'] is not None:
            sub_user.department_name = univercity_models.Department.objects.get(id=data['department_id'])
        
        if data['user_type'] == 'student':
            print('batch')
            sub_user.batch = None

    if 'staff_type' in data:
        if data['user_type'] == 'staff':
            if sub_user.staff_type != data['staff_type'] and data['staff_type'] is not None:
                sub_user.staff_type = data['staff_type']
            if data['staff_type']=='admin':
                user.is_staff = True
            else:
                user.is_staff = False

    user.save()
    sub_user.save()
