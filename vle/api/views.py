from rest_framework import response,status
from rest_framework.decorators import api_view,permission_classes
from . import serializer
from university import models as university_models
from django.http import HttpResponse
from Users import models as user_models
from . import permissions
from django.shortcuts import get_object_or_404
from Users import services as user_services


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
@permission_classes([permissions.IsFacultyAdminstrator])
def create_batch(request):
    new_batch = serializer.BatchSerializer(data=request.data)
    new_batch.is_valid(raise_exception=True)
    new_batch.save()
    return response.Response(new_batch.data,status=status.HTTP_201_CREATED)


@api_view(['PUT','PATCH'])
@permission_classes([permissions.IsFacultyAdminstrator])
def update_batch(request,id:int):
    batch = get_object_or_404(university_models.Batch,id=id)
    update = serializer.BatchSerializer(batch,data=request.data,partial=True)
    update.is_valid(raise_exception=True)
    update.save()
    return response.Response(update.data,status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsFacultyAdminstrator])
def delete_batch(request,id:int):
    batch = get_object_or_404(university_models.Batch,id=id)
    batch.delete()
    return response.Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminstrator])
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


@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminstrator])
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



@api_view(['POST'])
@permission_classes([permissions.IsFacultyAdminstrator])
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