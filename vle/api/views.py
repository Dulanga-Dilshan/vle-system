from rest_framework import response,status
from rest_framework.decorators import api_view,permission_classes
from . import serializer
from university import models as university_models
from Users import models as user_models
from . import permissions
from django.shortcuts import get_object_or_404
from Users import services as user_services
from config.config import get_setting,update_setting,get_all_setting
from rest_framework.exceptions import ValidationError,NotFound
from config import metrics
from config.middleware import get_avg_response_ms
from dashboard.annosments import mark_annoucements
from django.core.exceptions import PermissionDenied
from django.http import Http404
from dashboard.recent_activity import log_activity
from university import services as univercity_services

@api_view(['GET'])
def test_api(request):
    facultySerialize=serializer.FacultySerializer(university_models.Faculty.objects.all(),many=True)
    return response.Response(facultySerialize.data,status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([permissions.IsSuperUser])
def create_faculty(request):    
    new_faculty = serializer.FacultySerializer(data=request.data)
    new_faculty.is_valid(raise_exception=True)
    new_faculty.save()
    log_activity(actor=request.user,action=f"created new faculty '{new_faculty.data['name']}'")
    return response.Response(new_faculty.data,status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([permissions.IsSuperUser])
def delete_faculty(request,id):
    faculty = get_object_or_404(university_models.Faculty,id=id)
    name = faculty.name
    faculty.delete()
    log_activity(actor=request.user,action=f"deleted faculty {name}")
    return response.Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT','PATCH'])
@permission_classes([permissions.IsFacultyAdminstrator])
def update_faculty(request,id:int):
    faculty = get_object_or_404(university_models.Faculty,id=id)
    faculty_data = serializer.FacultySerializer(faculty,data=request.data,partial=True)
    faculty_data.is_valid(raise_exception=True)
    faculty_data.save()
    log_activity(actor=request.user,action=f"faculty {faculty.name} data updated ")
    return response.Response(faculty_data.data,status=status.HTTP_200_OK)


@api_view(['POST'])
def add_resource(request,faculty_id):
    resource = serializer.LectureHallSerializer(data=request.data)
    resource.is_valid(raise_exception=True)
    resource.save()
    return response.Response(resource.data,status=status.HTTP_201_CREATED)


@api_view(['PUT','PATCH'])
def update_resource(request,faculty_id,resource_id):
    try:
        univercity_services.update_resource(resource_id=resource_id,faculty_id=faculty_id,data=request.data)
    except ValidationError as e:
        return response.Response({'message':f'resource data invalid{e.detail}'},status=status.HTTP_400_BAD_REQUEST)
    except NotFound:
        return response.Response({'message':'resource not found'},status=status.HTTP_404_NOT_FOUND)
    
    return response.Response({},status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_resource(request,faculty_id,resource_id):
    resource = university_models.LectureHall.objects.filter(id=resource_id,faculty__id=faculty_id).first()
    if resource is None:
        return response.Response({'message':'resource not found'},status=status.HTTP_404_NOT_FOUND)
    
    resource.delete()
    return response.Response({},status=status.HTTP_204_NO_CONTENT)
    

@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminstrator])
def create_department(request):
    new_department = serializer.DepartmentSerializer(data=request.data)
    new_department.is_valid(raise_exception=True)
    new_department.save()
    log_activity(actor=request.user,action=f"new department {new_department.data['name']} created.")
    return response.Response(new_department.data,status=status.HTTP_201_CREATED)


@api_view(['PUT','PATCH'])
@permission_classes([permissions.IsFacultyAdminstrator])
def update_department(request,id):
    department  = get_object_or_404(university_models.Department,id=id)
    department_data = serializer.DepartmentSerializer(department,data=request.data,partial=True)
    department_data.is_valid(raise_exception=True)
    department_data.save()
    log_activity(actor=request.user,action=f"department {department.name} data updated ")
    return response.Response(department_data.data,status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsFacultyAdminstrator])
def delete_department(request,id):
    department = get_object_or_404(university_models.Department,id=id)
    department_name = department.name
    department.delete()
    log_activity(actor=request.user,action=f"department {department.name} deleted")
    return response.Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsBatchAdminstrator])
def create_batch(request):
    new_batch = serializer.BatchSerializer(data=request.data)
    new_batch.is_valid(raise_exception=True)
    new_batch.save()
    log_activity(actor=request.user,action=f"new batch {new_batch.name} added")
    return response.Response(new_batch.data,status=status.HTTP_201_CREATED)


@api_view(['PUT','PATCH'])
@permission_classes([permissions.IsBatchAdminstrator])
def update_batch(request,id:int):
    batch = get_object_or_404(university_models.Batch,id=id)
    update = serializer.BatchSerializer(batch,data=request.data,partial=True)
    update.is_valid(raise_exception=True)
    update.save()
    log_activity(actor=request.user,action=f"batch info updated")
    return response.Response(update.data,status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsBatchAdminstrator])
def delete_batch(request,id:int):
    batch = get_object_or_404(university_models.Batch,id=id)
    batch_name = batch.name
    batch.delete()
    log_activity(actor=request.user,action=f"batch {batch_name} removed")
    return response.Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT','PATCH'])
@permission_classes([permissions.IsBatchAdminstrator])
def add_students_to_batch(request,id):
    student_ids = request.data['student_ids']
    batch = get_object_or_404(university_models.Batch,id=id)
    for student_id in student_ids:
        student = get_object_or_404(user_models.Student,id=student_id)
        if student.department_name != batch.course.department:
            return response.Response({'massage':'not allowed on other departments'},status=status.HTTP_400_BAD_REQUEST)
        
        student.batch = batch
        student.save()
    
    return response.Response({'success': True,'added': len(student_ids),'message': f'Added {len(student_ids)} students to batch {batch.name}'},status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([permissions.IsBatchAdminstrator])
def remove_student_from_batch(request,id):
    student_ids = []
    if type(request.data['student_ids']) == list:
        student_ids=request.data['student_ids']
    else:
        student_ids.append(request.data['student_ids'])
    
    for student_id in student_ids:
        student = get_object_or_404(user_models.Student,id=student_id)
        student.batch = None
        student.save()

    batch = get_object_or_404(university_models.Batch,id=id)

    return response.Response({'success': True,'added': 1,'message': f'removed {len(student_ids)} students from batch {batch.name}'},status=status.HTTP_201_CREATED)



@api_view(['PUT','PATCH'])
@permission_classes([permissions.IsBatchAdminstrator])
def register_new_students(request,id):
    if not request.data['students']:
        return response.Response({'success': False,'added': 0,'message': 'no student data'},status=status.HTTP_400_BAD_REQUEST)

    students = request.data['students']
    batch = get_object_or_404(university_models.Batch,id=id)
    
    for student in students:
        user_data ={
            'username':student['student_id'],
            'email':student['email'],
            'full_name':student['full_name']
        }
        student_data={
            'name':student['full_name'],
            'username':student['student_id'],
            'faculty_id':batch.course.department.faculty.id,
            'department_id':batch.course.department.id,
            'batch_id':batch.id
        }
        
        if user_services.create_user_student(user_data,student_data) != True:
            return  response.Response({'message': 'incorrect data'},status=status.HTTP_400_BAD_REQUEST)
        
        log_activity(actor=request.user,action=f"registered new student {user_data['username']} to batch {batch.name}")
    
    return response.Response({'success': True,'added': len(students),'message': f'removed {len(students)} students from batch {batch.name}'},status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminstrator])
def create_user_student(request):
    count = 0
    for user in request.data['users']:
        user_data ={
            'username':user['username'],
            'email':user['email'],
            'full_name':user['name']
        }

        student_data={
            'name':user['name'],
            'username':user['username'],
            'faculty_id':user['faculty_id'],
            'department_id':user['department_id'],
            'batch_id': None
        }

        if user_services.create_user_student(user_data,student_data) != True:
            return  response.Response({'message': f"added {count}. unable to add {len(request.data['users'])-count}."},status=status.HTTP_400_BAD_REQUEST)
        
        log_activity(actor=request.user,action=f"registered new student {user_data['username']}")

        count += 1

    return response.Response({},status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminstrator])
def create_user_staff(request):
    count = 0
    for user in request.data['users']:
        user_data = {
            'username':user['username'],
            'email':user['email'],
            'full_name':user['name']
        }

        staff_data = {
            'name':user['name'],
            'username':user['username'],
            'staff_type':user['staff_type'],
            'faculty_id':user['faculty_id'],
            'department_id':user['department_id'],
        }
        count += 1
        if user_services.create_user_staff(user_data,staff_data) != True: 
            return  response.Response({'message': f"added {count}. unable to add {len(request.data['users'])-count}."},status=status.HTTP_400_BAD_REQUEST)

        log_activity(actor=request.user,action=f"registered new staff member {user_data['username']}")

    return response.Response({},status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminUserState])
def set_user_state(request):
    if not user_services.set_user_state(request.data['user_id'],request.data['action']):
        return response.Response({'message':'invalid ids'},status=status.HTTP_400_BAD_REQUEST)
    
    user = user_models.User.objects.filter(id=request.data['user_id']).first()
    if user:
        if request.data['action'] == 'suspend':
            request.data['action'] = 'suspended'
        else:
            request.data['action'] = 'activated'
        log_activity(actor=request.user,action=f"user account '{user.username}' is {request.data['action']}")
    
    return response.Response({},status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminUserState])
def bulk_user_status(request):
    user_ids = request.data['user_ids']
    for id in user_ids:
        if not user_services.set_user_state(id,request.data['action']):
            return response.Response({'message':'invalid id'},status=status.HTTP_400_BAD_REQUEST)
    
        user = user_models.User.objects.filter(id=request.data['user_id']).first()
        action = request.data['action']
        if action=='suspend':
            action += 'ed'
        else:
            action += 'd'
        log_activity(actor=request.user,action=f"user account '{user.username}' is {request.data['action']}")

    return response.Response({},status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminUserState])
def rest_user_psswd(request):
    if user_services.rest_passwd(request.data['user_id']):
        user = user_models.User.objects.filter(id=request.data['user_id']).first()
        log_activity(actor=request.user,action=f"password reseted user account {user.username}")
        return response.Response({},status=status.HTTP_201_CREATED)
    return response.Response({'message':'invalid id'},status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsFacultyAdminUserState])
def delete_user(request):
    username = user_models.User.objects.filter(id=request.data['user_id']).first().username
    if user_services.delete_user(request.data['user_id']):
        log_activity(actor=request.user,action=f"{username} account deleted")
        return response.Response({},status=status.HTTP_204_NO_CONTENT)
    return response.Response({'message':'invalid id'},status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminUserState])
def bulk_delete_users(request):
    user_ids = request.data['user_ids']
    for id in user_ids:
        if not user_services.delete_user(id):
            return response.Response({'message':'invalid id'},status=status.HTTP_400_BAD_REQUEST)
        
        user = user_models.User.objects.filter(id=id).first()
        if user is not None:
            log_activity(actor=request.user,action=f"{user.username} account deleted")

    return response.Response({},status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminUserState])
def update_user(request):
    try:
        user_services.update_user(request.data)
    except ValidationError:
        return response.Response({'message':'invalid data'},status=status.HTTP_400_BAD_REQUEST)
    except NotFound:
        return response.Response({'message':'user not found'},status=status.HTTP_404_NOT_FOUND)
    
    user =user_models.User.objects.filter(id=request.data['user_id']).first()
    log_activity(actor=request.user,action=f"{user.username} account updated")

    return response.Response({},status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminUserState])
def update_user_field(request):
    data = {
        'user_id':int(request.data['user_id']),
        'user_type':'staff' if 'user_type' not in request.data else request.data['user_type']
    }
    if 'field' in request.data:
        data[request.data['field']] = request.data['value']
    if 'faculty_id' in request.data:
        data['faculty_id']=request.data['faculty_id']
        data['department_id']=request.data['department_id']
    
    try:
        user_services.update_user(data)
    except ValidationError:
        return response.Response({'message':'invalid data'},status=status.HTTP_400_BAD_REQUEST)
    except NotFound:
        return response.Response({'message':'user not found'},status=status.HTTP_404_NOT_FOUND)
    
    user =user_models.User.objects.filter(id=request.data['user_id']).first()
    log_activity(actor=request.user,action=f"{user.username} account updated")

    return response.Response({},status=status.HTTP_201_CREATED)



@api_view(['GET'])
@permission_classes([permissions.IsAdmin])
def get_settings(request,key):
    try:
        value = get_setting(key)
    except KeyError:
        return response.Response({'detail':f"setting {key} dosn't exsits"},status=status.HTTP_404_NOT_FOUND)
    return response.Response({'value':value},status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAdmin])
def get_all_settings(request):
    return response.Response(get_all_setting(),status=status.HTTP_200_OK)


@api_view(['PUT','PATCH'])
@permission_classes([permissions.IsSuperUser])
def update_settings(request):
    try:
        settings = request.data['settings']
    except KeyError:
        return response.Response({'detail':"request is not in corroct format. expects {'settings':'[key:value]'}"},status=status.HTTP_400_BAD_REQUEST)
    
    for setting in settings:
        (key,value), = setting.items()
        old_value = get_setting(key)
        try:
            update_setting(key=key,value=value)
        except ValidationError as e:
            return response.Response({'detail':e.detail},status=status.HTTP_400_BAD_REQUEST)
        
        log_activity(actor=request.user,action=f"setting {key}  updated",content_info={key:old_value})
                
    return response.Response({'detail':f"settings updated"},status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAdmin])
def get_stats(request):
    try:
        cpu_and_net_io = metrics.get_net_io_cpu()
        stats = {
            'storage_usage':metrics.get_disk_usage(),
            'avg_response_time':round(get_avg_response_ms(),2),
            'system_up_time':metrics.format_time(metrics.get_system_up_time()),
            'memory_usage': metrics.memory_usage(),
            'cpu_usage':cpu_and_net_io["cpu_percent"],
            'net_down_bps':cpu_and_net_io["net_down_bps"],
            'net_up_bps':cpu_and_net_io["net_up_bps"]
        }
    except Exception as e:
        return response.Response({'detail':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response.Response(stats,status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def mark_annoucments(request):
    if 'announcement_ids' not in request.data:
        return response.Response({'detail':"request not in correct format!"},status=status.HTTP_400_BAD_REQUEST)
    
    ids = request.data['announcement_ids']
    for id in ids:
        try:
            mark_annoucements(request.user,int(id))
        
        except PermissionDenied:
            return response.Response({'detail':'no permission'},status=status.HTTP_403_FORBIDDEN)
        
        except Http404:
            return response.Response({'detail':'no permission'},status=status.HTTP_404_NOT_FOUND)

    return response.Response({'success': True},status=status.HTTP_200_OK)



@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def remove_annoucments(request):
    if 'announcement_ids' not in request.data:
        return response.Response({'detail':"request not in correct format!"},status=status.HTTP_400_BAD_REQUEST)
    
    ids = request.data['announcement_ids']
    for id in ids:
        try:
            mark_annoucements(user=request.user,annousment_id=int(id),as_delete=True)
        
        except PermissionDenied:
            return response.Response({'detail':'no permission'},status=status.HTTP_403_FORBIDDEN)
        
        except Http404:
            return response.Response({'detail':'no annousement'},status=status.HTTP_404_NOT_FOUND)

    return response.Response({'success': True},status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_batch_subjects(request,batch_id):
    try:
        univercity_services.populate_batch_subject(batch_id)
    except Http404 as e:
        return response.Response({'detail':str(e)},status=status.HTTP_404_NOT_FOUND)
    
    batch = university_models.Batch.objects.filter(id=batch_id).first()

    batch_subjects = university_models.BatchSubject.objects.filter(batch=batch)

    if batch_subjects is None or batch is None:
        return response.Response({},status=status.HTTP_404_NOT_FOUND)
    

    semesters = university_models.Semester.objects.filter(course=batch.course)
    semester_data = {}
    semester_data['batch_progress'] = str(batch.progression_year)
    semester_data['semesters'] = {}
    semester_data["teachers"]= []

    for semester in semesters:
        semester_subjects = university_models.BatchSubject.objects.filter(subject__semester=semester)
        semester_data['semesters'][str(semester.number)] = {
            "semester_code": str(semester.number),
            "display_name": f"Year {str(semester.number).split('.')[0]} - Semester {str(semester.number).split('.')[1]}",
            "status": univercity_services.get_semester_status(semester.number,batch.progression_year),
            "subjects" : univercity_services.get_subjects(semester_subjects),    
        }
    availble_teachers = user_models.Staff.objects.filter().exclude(staff_type='support')

    for availble_teacher in availble_teachers:
        semester_data["teachers"].append(
            {
                'id':availble_teacher.id,
                'name': availble_teacher.name,
                'email': availble_teacher.username.email,
                'department': availble_teacher.department_name.name
            }
        )

    return response.Response(semester_data,status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsValiedAssignment])
def assign_lecture(request):

    batch_subject = university_models.BatchSubject.objects.filter(batch__id=request.data['batch_id'],subject__id=request.data['subject_id']).first()
    if not batch_subject:
        return response.Response({'detail':"invalid assignment"},status=status.HTTP_400_BAD_REQUEST)
    
    staff = user_models.Staff.objects.filter(id=request.data['teacher_id']).exclude(staff_type='support').first()
    batch_subject.staff = staff
    batch_subject.save()
    return response.Response({},status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminAdvanceBatch])
def advance_batch(request,batch_id):
    batch = university_models.Batch.objects.filter(id=batch_id).first()
    if batch is None:
        return response.Response({'detail':"invalid batch"},status=status.HTTP_400_BAD_REQUEST)
    
    if float(batch.progression_year) == 4.2:
        return response.Response({},status=status.HTTP_200_OK)
    
    from university.models import semesters

    if float(batch.progression_year) not in semesters:
        return response.Response({'detail':"invalid semester"},status=status.HTTP_400_BAD_REQUEST)
    
    batch.progression_year = semesters[ semesters.index(float(batch.progression_year)) +1 ]
    batch.save()

    return response.Response({},status=status.HTTP_200_OK)

@api_view(['GET'])
def get_schedules(request,batch_id):
    schedule = {
        'shedules':{
            'monday':[
                {
                    'id':1,
                    'start_time':'08.00am',
                    'end_time':'09.00am',
                    'subject':{
                        'id': 1,
                        'name':'subject name',
                        'code':'sub code',
                        'teacher':{
                            'id': 1,
                            'name':'teacher name'
                        },
                        'substitute_teacher':{
                            'id': 1,
                            'name':'substitute teacher'
                        }
                    },
                    'hall':{
                        'id':1,
                        'type':'type'
                    }
                },
                {
                    'id':4,
                    'start_time':'10.00am',
                    'end_time':'11.00am',
                    'subject':{
                        'id': 4,
                        'name':'subject name',
                        'code':'sub code',
                        'teacher':{
                            'id': 6,
                            'name':'teacher name'
                        },
                        'substitute_teacher':None
                    },
                    'hall':{
                        'id':1,
                        'type':'type'
                    }
                }
            ],
            'tuesday':[
                {
                    'id':7,
                    'start_time':'10.00am',
                    'end_time':'12.00pm',
                    'subject':{
                        'id': 7,
                        'name':'subject name',
                        'code':'sub code',
                        'teacher':{
                            'id': 9,
                            'name':'teacher name'
                        },
                        'substitute_teacher':None
                    },
                    'hall':{
                        'id':1,
                        'type':'type'
                    }
                },
                {
                    'id':21,
                    'start_time':'10.00am',
                    'end_time':'11.00am',
                    'subject':{
                        'id': 4,
                        'name':'subject name',
                        'code':'sub code',
                        'teacher':{
                            'id': 6,
                            'name':'teacher name'
                        },
                        'substitute_teacher':None
                    },
                    'hall':{
                        'id':1,
                        'type':'type'
                    }
                }
            ]
        }
    }
    return response.Response(schedule,status=status.HTTP_200_OK)