from . import models
from django.http.request import QueryDict
from django.shortcuts import get_object_or_404

def add_course(POST:QueryDict)-> bool:
    name = POST.get('course_name')
    code = POST.get('course_code')
    duration_years=int(POST.get('durationyears'))
    department = get_object_or_404(models.Department,id=int(POST.get('department')))
    description = POST.get('description')

    if models.Course.objects.filter(code=code).exists():
        return False    

    if  duration_years < 1:
        return False
    
    new_course  = models.Course(
        code = code,
        name = name,
        department = department,
        duration_years = duration_years,
        description = description
    )

    try:
        new_course.save()
    except Exception as e:
        print(e)
        return False
    
def get_course_count()->int:
    return models.Course.objects.count()


def department_count(faculty_id:int=None)->int:
    if faculty_id:
        return models.Department.objects.filter(faculty=faculty_id).count()
    
    return models.Department.objects.all().count()


    



    