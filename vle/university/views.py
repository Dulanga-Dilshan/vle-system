from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from Users import models as user_models
from django.db.models import Prefetch
from . import models as university_models,services as university_services
from django.http.request import QueryDict
from django.http import HttpResponse
from Users import services as user_services

@login_required(login_url='Users:login')
def manage_course(request,id):
    user = request.user
    if user.is_staff == 0:
        return redirect('dashboard:route')
    if user.role == 'staff':
        user_faculty = user_models.Staff.objects.get(username=user.id).faculty_name
        course_faculty = university_models.Course.objects.get(id=id).department.faculty
        if course_faculty!=user_faculty:
            return redirect('dashboard:route')

    context = {}

    course = university_models.Course.objects.prefetch_related(
        Prefetch('semesters',queryset=university_models.Semester.objects.prefetch_related('subjects'))
    ).get(id=id)


    if len(course.semesters.all())<4:
        context['footer'] = True

    context['course']=course

    return render(request,'dashboard/admin/manage_course.html',context)

@login_required(login_url='Users:login')
def add_subject(request):
    if request.user.is_staff == 0:
        return redirect('dashboard:route')
    
    course = get_object_or_404(university_models.Course,id=request.POST.get('course_id'))
    semester = get_object_or_404(university_models.Semester,id=request.POST.get('semester_id'))
    department = get_object_or_404(university_models.Department,id=request.POST.get('department_id'))
    subject_code = request.POST.get('code')
    subject_name = request.POST.get('name')
    subject_credits = request.POST.get('credits')
    subject_hours = request.POST.get('total_hours')
    
    if request.user.role == 'staff':
        user_faculty = user_models.Staff.objects.get(username=request.user.id).faculty_name
        course_faculty = university_models.Course.objects.get(id=course.id).department.faculty
        if course_faculty!=user_faculty:
            return redirect('dashboard:route')
    
    if not university_models.Subject.objects.filter(code=subject_code).exists():
        new_subject = university_models.Subject(
            department = department,
            course = course,
            semester = semester,
            code = subject_code,
            name = subject_name,
            credits = subject_credits,
            total_hours = subject_hours
        )
        try:
            new_subject.save()
        except Exception as e:
            print(e)
    
    return redirect('dashboard:manage_course',id=course.id)




@login_required(login_url='Users:login')
def delete_subject(request:QueryDict,id:int)->HttpResponse:
    if request.user.is_staff == 0:
        return HttpResponse('no permissions',status=400)
    
    if request.user.role == 'staff':
        user_faculty = user_models.Staff.objects.get(username=request.user.id).faculty_name
        subject_faculty = university_models.Subject.objects.get(id=id).department.faculty

        if user_faculty != subject_faculty:
            return HttpResponse('no permissions',status=400)
    
    subject = get_object_or_404(university_models.Subject,id=id)
    subject.delete()

    return HttpResponse('sucsess',status=200)


@login_required(login_url='Users:login')
def add_semester(request:QueryDict):
    cource = university_models.Course.objects.get(id=request.POST.get('course_id'))
    if request.POST.get('number') == "":
        return redirect('dashboard:manage_course',id=cource.id)
    
    number =int(request.POST.get('number'))
    
    
    if request.user.is_staff == 0:
        return redirect('dashboard:manage_course',id=cource.id)
    
    if request.user.role == 'staff':
        user_faculty = user_models.Staff.objects.get(username=request.user.id).faculty_name
        cource_faculty = university_models.Course.objects.get(id=id).department.faculty

        if user_faculty!=cource_faculty:
            return redirect('dashboard:manage_course',id=cource.id)
        

    if number>10:
        return redirect('dashboard:manage_course',id=cource.id)
    
    new_semester = university_models.Semester(
        course = cource,
        number = number
    )

    try:
        new_semester.save()
    except Exception as e:
        print(e)
    
    return redirect('dashboard:manage_course',id=cource.id)
    
@login_required(login_url='Users:login')
def update_subject(request):
    if request.method == 'POST':
        subject = get_object_or_404(university_models.Subject,id=request.POST.get('subject_id'))
        if request.user.is_staff == 0:
            return redirect('dashboard:route')
        
        if request.user.role == 'staff':
            user_faculty = user_models.Staff.objects.get(username=request.user.id).faculty_name
            subject_faculty = subject.course.department.faculty

            if user_faculty!=subject_faculty:
                return redirect('dashboard:manage_course',id=subject.cource.id)
        
        if subject.name != request.POST.get('name') and request.POST.get('name') != '':
            subject.name=request.POST.get('name')
        
        if subject.credits != request.POST.get('credits') and request.POST.get('credits') != '':
            subject.credits = request.POST.get('credits')
        
        if subject.total_hours != request.POST.get('total_hours') and request.POST.get('total_hours') != None:
            subject.total_hours = request.POST.get('total_hours')

        try:
            subject.save()
        
        except Exception as e:
            print(e)
    
        return redirect('dashboard:manage_course',id=subject.course.id)
    
    return redirect('dashboard:route')

@login_required(login_url='Users:login')
def manage_faculties(request):
    if request.user.is_staff == 0:
        return redirect('dashboard:route')
    context = {}
    context['faculties'] = university_models.Faculty.objects.all()
    context['total_departments'] = university_services.department_count()

    if request.user.role == 'staff':
        user = user_models.Staff.objects.get(username=request.user)
        context['faculties'] = context['faculties'].filter(id=user.id)
        context['total_departments'] = university_services.department_count(faculty_id=user.faculty_name)

    context['total_faculty_members'] = user_services.user_count(admins=False)
    context['available_deans'] = user_models.Staff.objects.all()

    return render(request,'dashboard/admin/manage_faculties.html',context)


@login_required(login_url='Users:login')
def manage_faculty(request,id:int):
    contex = {}
    contex['faculty'] = university_models.Faculty.objects.filter(id=id).first()
    contex['departments'] = university_models.Department.objects.filter(faculty=id)
    contex['available_hods'] = user_models.Staff.objects.filter(faculty_name=id)
    return render(request,'dashboard/admin/manage_faculty.html',contex)


def manage_batches(request):
    contex = {}
    contex['courses']=university_models.Course.objects.all()
    contex['batches']=university_models.Batch.objects.all()
    contex['active_students_count']=user_models.Student.objects.exclude(batch=None).__len__
    return render(request,'dashboard/admin/manage_batches.html',contex)


def manage_batch(request,id:int):
    context = {}
    context['batch'] = get_object_or_404(university_models.Batch,id=id)
    context['students'] = user_models.Student.objects.filter(batch=id)
    
    context['all_students'] = user_models.Student.objects.filter(department_name=context['batch'].course.department).exclude(batch=context['batch'])
    
    return render(request,'dashboard/admin/manage_batch.html',context)