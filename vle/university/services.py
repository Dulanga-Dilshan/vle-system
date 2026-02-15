from . import models
from django.http.request import QueryDict
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError
from django.db import transaction


@transaction.atomic
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
    
    return True
    
def get_course_count()->int:
    return models.Course.objects.count()


def department_count(faculty_id:int=None)->int:
    if faculty_id:
        return models.Department.objects.filter(faculty=faculty_id).count()
    
    return models.Department.objects.all().count()

@transaction.atomic
def populate_batch_subject(batch_id:int):
    batch = models.Batch.objects.filter(id=batch_id).first()
    if batch is None:
        raise NotFound('invalid batch id')
    
    subjects = models.Subject.objects.filter(course=batch.course).order_by('semester')
    if subjects is None:
        raise NotFound(f'no subjects at the moment for the course {batch.course.name}')
    
    for subject in subjects:
        obj , created = models.BatchSubject.objects.get_or_create(
            batch = batch,
            subject = subject
        )

def get_semester_status(semester_number:float,current_semester:float) -> str:
    if current_semester == semester_number:
        return "current"
    
    elif current_semester > semester_number:
        return "completed"
    
    return "upcoming"

def get_subjects(semester_subjects)->list:
    subjects = []

    for semester_subject in semester_subjects:
        subject = {}
        subject['id'] = semester_subject.subject.id
        subject['name'] = semester_subject.subject.name
        subject['code'] = semester_subject.subject.code

        #print(subject['id'],subject['name'],subject['code'])
        if semester_subject.staff == None:
            subject['assigned_teacher'] = None
        else:
            subject['assigned_teacher'] = {
                "id": semester_subject.staff.id,
                "name": semester_subject.staff.name,
                "email": semester_subject.staff.username.email,
            }
        subjects.append(subject)
        
    return subjects

@transaction.atomic
def update_resource(resource_id:int,faculty_id:int,data:dict)->None:
    resource = models.LectureHall.objects.filter(id=resource_id,faculty__id=faculty_id).first()
    if resource is None:
        raise NotFound('invalide resource')
    

    data['name'] = data['name'].strip()
    if len(data['name']) < 1:
        raise ValidationError('name cant be empty')
    if len(data['name']) > 50:
        raise ValidationError('name cant more than 50 chars')
    
    for key,_ in models.LectureHall.HALL_TYPE:
        if key==data['hall_type']:
            break
    else:
        raise ValidationError(f'not a valid hall type.{models.LectureHall.HALL_TYPE}')
        
    if data['capacity'] < 1 or  data['capacity'] >1000:
        raise ValidationError(f'capacity must be in 1-1000. got {data['capacity']}')
    
    if resource.name != data['name']:
        resource.name = data['name']

    if resource.hall_type != data['hall_type']:
        resource.hall_type = data['hall_type']

    if resource.capacity != data['capacity']:
        resource.capacity = data['capacity']
    
    resource.save()
