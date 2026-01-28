from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from Users import models,services
from university import models as university_models
from university import services as university_services
from . import annosments
from django.http import HttpResponse


def get_name_avatar(request):
    if request.user.first_name=="" or request.user.last_name=="":
        name = request.user.username
        avetar = name[:2]
    else:
        name = f"{request.user.first_name}  {request.user.last_name}"
        avetar = f"{request.user.first_name[:1]}{request.user.last_name[:1]}"

    return {'name':name,'avetar':avetar}

#student veiw
@login_required(login_url='Users:login')
def student(request):
    if request.user.role != 'student':
        return redirect('dashboard:route')
    
    contex=get_name_avatar(request)
    return render(request,"dashboard/student/student.html",contex)


#staff veiw
@login_required(login_url='Users:login')
def staff(request):
    if request.user.role != 'staff':
        return redirect('dashboard:route')

    contex=get_name_avatar(request)
    return render(request,"dashboard/staff/staff.html",contex)


#admin veiw
@login_required(login_url='Users:login')
def admin(request):
    contex=get_name_avatar(request)
    
    if request.user.is_staff == 0:
        return redirect('dashboard:route')
    
    contex['request_count'] = services.get_request_count()
    contex['user_presentage'] = f"{round((services.user_count() / services.max_user_count()) *100,2) }%"
    contex['user_count'] = services.user_count()
    contex['course_count'] = university_services.get_course_count()
    
    return render(request,"dashboard/admin/admin.html",contex)

@login_required(login_url='Users:login')
def route(request):
    role = request.user.role
    if role=='student':
        return redirect('dashboard:student')
    
    elif role=='staff':
        staff=models.Staff.objects.get(username=request.user)
        if not staff:
            return redirect('Users:login')

        if staff.staff_type == 'admin':
            return redirect('dashboard:admin')
        
        return redirect('dashboard:staff')
    
    elif role=='admin':
        return redirect('dashboard:admin')
    
    else:
        return redirect('Users:login_user')




@login_required(login_url='Users:login')
def manage_register_requests(request):
    if not services.check_permission_administater(request.user):
        return redirect('dashboard:route')
    
    contex={}

    if request.user.role == 'admin':
        StudentRegistretionRequests= models.StudentRegistretionRequest.objects.all()
        StaffRegistretionRequests = models.StaffRegistretionRequest.objects.all()
    elif request.user.role == 'staff':
        user = models.Staff.objects.get(username=request.user)
        StudentRegistretionRequests = models.StudentRegistretionRequest.objects.filter(faculty_name=user.faculty_name)
        StaffRegistretionRequests = models.StaffRegistretionRequest.objects.filter(faculty_name=user.faculty_name)

    contex['students']=StudentRegistretionRequests
    contex['staff']=StaffRegistretionRequests


    return render(request,"dashboard/admin/manage_registration_requests.html",contex)


@login_required(login_url='Users:login')
def manage_student_register_requests(request):
    if not services.check_permission_administater(request.user):
        return redirect('dashboard:route')
    
    if request.method == 'POST':
        if request.user.role == 'admin':
            students = models.StudentRegistretionRequest.objects.all()
        elif request.user.role == 'staff':
            user = models.Staff.objects.get(username=request.user)
            students = models.StudentRegistretionRequest.objects.filter(faculty_name=user.faculty_name)
        
        approved = []
        denied = []
        action = ''

        for student in students:
            action = request.POST.get(str(student.id))
            if action == 'approved':
                approved.append(student.id)
            elif action == 'denied':
                denied.append(student.id)
        
        try:
            services.approve_register_request(approved,'student')
            services.delete_ragistration_requests(denied,'student')
        
        except Exception as e:
            print(e)

    return redirect('dashboard:manage_requests')

@login_required(login_url='Users:login')
def manage_staff_register_requests(request):
    if not services.check_permission_administater(request.user):
        return redirect('dashboard:route')
    
    if request.method == 'POST':
        if request.user.role == 'admin':
            staff = models.StaffRegistretionRequest.objects.all()
        elif request.user.role == 'staff':
            user = models.Staff.objects.get(username=request.user)
            staff = models.StudentRegistretionRequest.objects.filter(faculty_name=user.faculty_name)
        
        approved = []
        denied = []
        action = ''

        for stf in staff:
            action = request.POST.get(str(stf.id))
            if action == 'approved':
                approved.append(stf.id)
            elif action == 'denied':
                denied.append(stf.id)

        try:
            services.approve_register_request(approved,'staff')
            services.delete_ragistration_requests(denied,'staff')
        
        except Exception as e:
            print(e)

    return redirect('dashboard:manage_requests')

@login_required(login_url='Users:login')
def manage_users(request):
    if not services.check_permission_administater(request.user):
        return redirect('dashboard:route')
    
    if request.user.role == 'admin':
        students = models.Student.objects.select_related('username')
        staff = models.Staff.objects.select_related('username')
    elif request.user.role == 'staff':
        user = models.Staff.objects.get(username=request.user)
        students = models.Student.objects.select_related('username').filter(faculty_name=user.faculty_name)
        staff = models.Staff.objects.select_related('username').filter(faculty_name=user.faculty_name)

    contex={}
    contex['students']=students
    contex['staff'] = staff
    contex['faculties'] = university_models.Faculty.objects.all()
    contex['departments'] = university_models.Department.objects.all()


    return render(request,"dashboard/admin/manage_users.html",contex)

@login_required(login_url='Users:login')
def manage_courses(request):
    if not services.check_permission_administater(request.user):
        return redirect('dashboard:route')
    
    errors = []

    courses = university_models.Course.objects.select_related("department","department__faculty")
    departments = university_models.Department.objects.select_related("faculty")

    try:
        faculty_id = int(request.GET.get('faculty'))
    except (ValueError , TypeError):
        faculty_id = None

    
    try:
        department_id = int(request.GET.get('department'))
    except (ValueError,TypeError):
        department_id = None


    if request.user.role == 'admin':
        if faculty_id:
            courses=courses.filter(department__faculty = faculty_id)
            departments=departments.filter(faculty=faculty_id)
        
        if department_id:
            courses=courses.filter(department=department_id)
            departments=departments.filter(id=department_id)
    
    elif request.user.role == 'staff':
        user = models.Staff.objects.get(username=request.user)
        courses = courses.filter(department__faculty=user.faculty_name)
        departments = departments.filter(faculty=user.faculty_name)
    

    context = {
        'courses':courses,
        'departments':departments
    }

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update':
            for course in context['courses']:
                if course.id == int(request.POST.get('id')):
                    if course.name != request.POST.get('course_name') or course.duration_years != request.POST.get('durationyears'):
                        course.name = request.POST.get('course_name')

                        if course.description !=  request.POST.get('description'):
                            course.description=request.POST.get('description')

                        if 10 > int(request.POST.get('durationyears')) > 0:
                            course.duration_years = request.POST.get('durationyears')
                        
                        try:
                            course.save()
                        except Exception as e:
                            print(e)

        if action == 'delete':
            for course in context['courses']:
                if course.id == int(request.POST.get('id')):
                    course.delete()
                    context['courses']=university_models.Course.objects.all()
        
        if action == 'add':
            if not university_services.add_course(request.POST):
                errors.append('couldnt able to add new course')
            
    context['error']=errors
    return render(request,'dashboard/admin/manage_courses.html',context)


def system_state(request):
    return render(request,'dashboard/admin/system_stats.html')




def system_settings(request):
    return render(request,'dashboard/admin/system_settings.html')


