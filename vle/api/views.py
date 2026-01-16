from rest_framework import response,status
from rest_framework.decorators import api_view,permission_classes
from . import serializer
from university import models as university_models
from django.http import HttpResponse
from Users import models as user_models
from . import permissions
from django.shortcuts import get_object_or_404

# Create your views here.


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