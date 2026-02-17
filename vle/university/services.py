from . import models
from django.http.request import QueryDict
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError
from django.db import transaction
from Users.models import Staff


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


def validate_time(time:str)->bool:
    parts = time.split('.')
    hour = parts[0]
    minuts = parts[1][:2]
    meridiem = parts[1][2:4]

    if int(hour) < 0 or int(hour) >12:
        return False
    
    if int(minuts)<0 or int(minuts)>60:
        return False
    
    if not (meridiem=='am' or meridiem=='pm'):
        return False
    
    return True

@transaction.atomic
def create_schedule(data:dict):
    batch_subject = models.BatchSubject.objects.filter(batch__id=data['batch_id'],id=data['batch_subject_id']).first()
    if batch_subject is None:
        raise NotFound('invalide subject')
    
    hall = models.LectureHall.objects.filter(id=data['hall_id'],faculty=batch_subject.batch.course.department.faculty).first()
    if hall is None:
        raise NotFound('invalide Lecture Hall')
    
    substitute_teacher = Staff.objects.filter(id=data['substitute_teacher_id'],faculty_name=batch_subject.batch.course.department.faculty).first()
    if not substitute_teacher and data['substitute_teacher_id']:
        raise NotFound('invalide substitute teacher')
    
    all_shedules = models.Schedule.objects.filter(subject=batch_subject,day=data['day'])
    for shedule in all_shedules:
        if is_between_time(shedule.start_time,shedule.end_time,data['start_time']):
            raise NotFound('invalid time slot')
    
    for _,day in models.Schedule.DAYS:
        if day == data['day']:
            break
    else:
        raise ValidationError(f'not a valid day.{models.Schedule.DAYS}')
    
    
    times = [data['start_time'],data['end_time']]

    for time in times:
        if not validate_time(time):
            raise ValidationError(f'not a valid time format. (8.00pm)')
        
    data['notes'].strip()
    if len(data['notes']) >100:
        raise ValidationError(f'not a valid note. max len 100')


    schedule = models.Schedule(
        subject = batch_subject,
        hall = hall,
        substitute_teacher = substitute_teacher,
        day = day,
        start_time = data['start_time'],
        end_time = data['end_time'],
        notes = data['notes']
    )

    try:
        schedule.save()
    except Exception as e:
        raise ValidationError(f'data is invalid')

def get_shedules(batch_id:int)->dict:
    shedule_objs = models.Schedule.objects.filter(subject__batch__id=batch_id)
    if shedule_objs is None:
        raise NotFound('no shedukes for the batch')
    shedules = {}

    for _,day in models.Schedule.DAYS:
        objs  = shedule_objs.filter(day=day)
        shedules[day]=[]
        for obj in objs:
            shedule = {
                'id' : obj.id,
                'start_time':obj.start_time,
                'end_time':obj.end_time,
                'subject':{
                    'id':obj.subject.subject.id,
                    'name':obj.subject.subject.name,
                    'code':obj.subject.subject.code,
                    'teacher':None if obj.subject.staff is None else{
                        'id':obj.subject.staff.id,
                        'name':obj.subject.staff.name,
                    },
                    'substitute_teacher':None if obj.substitute_teacher is None else {          
                        'id':obj.substitute_teacher.id,
                        'name':obj.substitute_teacher.name,
                    },
                    'notes':obj.notes,
                },
                'hall':{
                    'id':obj.hall.id,
                    'name':obj.hall.name,
                    'type':obj.hall.hall_type,
                }
            }
            shedules[day].append(shedule)
    
    return {'shedules':shedules}

def get_availble_halls(batch_id:int,data:dict)->dict:

    times = [data['start_time'],data['end_time']]

    for time in times:
        if not validate_time(time):
            raise ValidationError(f'not a valid time format.')
        
    batch = models.Batch.objects.filter(id=batch_id).first()
    if batch is None:
        raise NotFound('invalide batch')
    

    
    all_hall_objs = models.LectureHall.objects.filter(faculty=batch.course.department.faculty)
    shedule_objs = models.Schedule.objects.filter(subject__batch=batch,day=data['day'])

    available_halls = []

    for hall_obj in all_hall_objs:
        for shedule_obj in shedule_objs:
            if hall_obj==shedule_obj.hall:
                if not is_between_time(shedule_obj.start_time,shedule_obj.end_time,data['start_time']):
                    available_halls.append(
                        {
                            'id':hall_obj.id,
                            'name':hall_obj.name,
                            'type':hall_obj.hall_type,
                            'capacity':hall_obj.capacity,
                        }
                    )
                    break
            else:
                available_halls.append(
                        {
                            'id':hall_obj.id,
                            'name':hall_obj.name,
                            'type':hall_obj.hall_type,
                            'capacity':hall_obj.capacity,
                        }
                    )
                break
        else:
            available_halls.append(
                        {
                            'id':hall_obj.id,
                            'name':hall_obj.name,
                            'type':hall_obj.hall_type,
                            'capacity':hall_obj.capacity,
                        }
                    )
    return {'available_halls':available_halls}
        
    
def is_between_time(start_time:str,end_time:str,new_time:str)->bool:
    times = [start_time,end_time,new_time]
    times_in_float = []
    for time in times:
        parts = time.split('.')
        h = float(parts[0])
        m = float(parts[1][:2])
        mi = parts[1][2:4]
        if mi=='pm':
            h+=12
        if m != 0:
            h+= m/100
        times_in_float.append(h)
    
    if times_in_float[0]<times_in_float[2] and times_in_float[1] > times_in_float[2]:
        return True
    
    return False


@transaction.atomic
def update_shedule(schedule_id,data:dict)->None:
    schedule = models.Schedule.objects.filter(id=schedule_id).first()
    if schedule is None:
        raise NotFound('invalide shedule')
    
    batch_subject = models.BatchSubject.objects.filter(id=data['subject_id']).first()
    if batch_subject is None:
        raise NotFound('invalide subject')
    
    if schedule.subject != batch_subject:
        raise ValidationError('invalid subject')
    
    substitute_teacher = Staff.objects.filter(id=data['substitute_teacher_id']).first()
    if data['substitute_teacher_id'] is not None:
        if substitute_teacher is None:
            raise NotFound('substitute teacher not found')
        
    lec_hall = models.LectureHall.objects.filter(id=data['hall_id']).first()

    data['notes']=data['notes'].strip()
    if len(data['notes'])>100:
        raise ValidationError('max lenth exseeded. max=100chars')


    if schedule.subject != batch_subject:
        schedule.subject = batch_subject
    
    if schedule.substitute_teacher != substitute_teacher:
        schedule.substitute_teacher=substitute_teacher
    
    if schedule.hall != lec_hall:
        schedule.hall = lec_hall
    
    if schedule.notes != data['notes']:
        schedule.notes = data['notes']
    
    schedule.save()