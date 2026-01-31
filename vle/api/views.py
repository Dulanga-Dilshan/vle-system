from rest_framework import response,status
from rest_framework.decorators import api_view,permission_classes
from . import serializer
from university import models as university_models
from django.http import HttpResponse
from Users import models as user_models
from . import permissions
from django.shortcuts import get_object_or_404
from Users import services as user_services
from config.config import get_setting,update_setting,get_all_setting


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
    return response.Response(new_faculty.data,status=status.HTTP_201_CREATED)



@api_view(['DELETE'])
@permission_classes([permissions.IsSuperUser])
def delete_faculty(request,id):
    faculty = get_object_or_404(university_models.Faculty,id=id)
    faculty.delete()
    return response.Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['PUT','PATCH'])
@permission_classes([permissions.IsFacultyAdminstrator])
def update_faculty(request,id:int):
    faculty = get_object_or_404(university_models.Faculty,id=id)
    faculty_data = serializer.FacultySerializer(faculty,data=request.data,partial=True)
    faculty_data.is_valid(raise_exception=True)
    faculty_data.save()
    return response.Response(faculty_data.data,status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminstrator])
def create_department(request):
    new_department = serializer.DepartmentSerializer(data=request.data)
    new_department.is_valid(raise_exception=True)
    new_department.save()
    return response.Response(new_department.data,status=status.HTTP_201_CREATED)


@api_view(['PUT','PATCH'])
@permission_classes([permissions.IsFacultyAdminstrator])
def update_department(request,id):
    department  = get_object_or_404(university_models.Department,id=id)
    department_data = serializer.DepartmentSerializer(department,data=request.data,partial=True)
    department_data.is_valid(raise_exception=True)
    department_data.save()
    return response.Response(department_data.data,status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsFacultyAdminstrator])
def delete_department(request,id):
    department = get_object_or_404(university_models.Department,id=id)
    department.delete()
    return response.Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsBatchAdminstrator])
def create_batch(request):
    new_batch = serializer.BatchSerializer(data=request.data)
    new_batch.is_valid(raise_exception=True)
    new_batch.save()
    return response.Response(new_batch.data,status=status.HTTP_201_CREATED)


@api_view(['PUT','PATCH'])
@permission_classes([permissions.IsBatchAdminstrator])
def update_batch(request,id:int):
    batch = get_object_or_404(university_models.Batch,id=id)
    update = serializer.BatchSerializer(batch,data=request.data,partial=True)
    update.is_valid(raise_exception=True)
    update.save()
    return response.Response(update.data,status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsBatchAdminstrator])
def delete_batch(request,id:int):
    batch = get_object_or_404(university_models.Batch,id=id)
    batch.delete()
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

    return response.Response({},status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminUserState])
def set_user_state(request):
    if not user_services.set_user_state(request.data['user_id'],request.data['action']):
        return response.Response({'message':'invalid ids'},status=status.HTTP_400_BAD_REQUEST)
    
    return response.Response({},status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminUserState])
def bulk_user_status(request):
    user_ids = request.data['user_ids']
    for id in user_ids:
        if not user_services.set_user_state(id,request.data['action']):
            return response.Response({'message':'invalid id'},status=status.HTTP_400_BAD_REQUEST)
    
    return response.Response({},status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminUserState])
def rest_user_psswd(request):
    if user_services.rest_passwd(request.data['user_id']):
        return response.Response({},status=status.HTTP_201_CREATED)
    return response.Response({'message':'invalid id'},status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([permissions.IsFacultyAdminUserState])
def delete_user(request):
    if user_services.delete_user(request.data['user_id']):
        return response.Response({},status=status.HTTP_204_NO_CONTENT)
    return response.Response({'message':'invalid id'},status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminUserState])
def bulk_delete_users(request):
    user_ids = request.data['user_ids']
    for id in user_ids:
        if not user_services.delete_user(id):
            return response.Response({'message':'invalid id'},status=status.HTTP_400_BAD_REQUEST)

    return response.Response({},status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminUserState])
def update_user(request):
    user_services.update_user(request.data)
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
    
    user_services.update_user(data)
    return response.Response({},status=status.HTTP_201_CREATED)



@api_view(['GET'])
@permission_classes([permissions.IsSuperUser])
def get_settings(request,key):
    try:
        value = get_setting(key)
    except KeyError:
        return response.Response({'detail':f"setting {key} dosn't exsits"},status=status.HTTP_404_NOT_FOUND)
    return response.Response({'value':value},status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsSuperUser])
def get_all_settings(request):
    return response.Response(get_all_setting(),status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([permissions.IsSuperUser])
def update_settings(request):
    #update_setting(key=request.data.key,value=request.data.value)
    return response.Response({'detail':f"setting {'key'} dosn't exsits"},status=status.HTTP_406_NOT_ACCEPTABLE)



#{'key': 'SYSTEM_NAME', 'value': 'UOV VL'}