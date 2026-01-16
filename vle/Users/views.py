from django.shortcuts import render,HttpResponse,redirect
from .models import User,StudentRegistretionRequest,StaffRegistretionRequest
from django.contrib.auth import authenticate,login,logout
from django.conf import settings
from university.models import Faculty,Department
from django.db.models import Q
from django.db import IntegrityError
from django.http import JsonResponse
from django.core.validators import validate_email,validate_image_file_extension
from django.core.exceptions import ValidationError
from PIL import Image



def test(request):
    if request.method == "POST":
        user=request.POST.get('usr')
        email=request.POST.get('email')
        try:
            usr = User.objects.get(username=user)
            return HttpResponse("user exsist")
        except:
            return HttpResponse("user don't exsist")


    return render(request,'Users/test.html')



def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user= User.objects.get(username=username)
        except:
            return render(request,"Users/login.html",{'error':'wrong username','errno':'1' })
        
        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user) 

            if request.POST.get('remember_me')=='1':
                request.session.set_expiry(getattr(settings, 'SESSION_EXPIRE', 60 * 60 * 24 * 1))
            else:
                request.session.set_expiry(0)

            return redirect('dashboard:route')

        return render(request,"Users/login.html",{'error':'wrong password','errno':'2' })
    
    return render(request,"Users/login.html")

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    
    return redirect('Users:login')

def register_user(request):
    faculties  = Faculty.objects.all()
    departments = Department.objects.all()
    if request.method == 'POST':
        role = request.POST.get('role')
        faculty = Faculty.objects.get(id=request.POST.get('faculty'))
        department = Department.objects.get(id = request.POST.get('department'))
        email = request.POST.get('email')
        passwd = request.POST.get('passwd')

        if role=='student':
            username = request.POST.get('stu_id')
        elif role=='staff': 
            username = request.POST.get('stf_id')


        errors = {}

        if len(passwd) < 6:
            errors['passwd']='password is too short'
        
        try:
            validate_email(email)
        except ValidationError:
            errors['email']="invalid email"




        if errors:
            return render(request,"Users/register.html",{'faculties':faculties,'departments':departments,'errors':errors})
        
        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            errors['user_exsits']="username or email already in use"
        
        if StudentRegistretionRequest.objects.filter(Q(username=username) | Q(email=email)).exists():
            errors['user_pending_std']="username or email already in use"

        if StaffRegistretionRequest.objects.filter(Q(username=username) | Q(email=email)).exists():
            errors['user_pending_stf']="username or email already in use"
        
        if errors:
            return render(request,"Users/register.html",{'faculties':faculties,'departments':departments,'errors':errors})
        

        if role == "student":
            first_name = request.POST.get('fname')
            last_name = request.POST.get('lname')
            id_img = request.FILES.get('idImg')
            if id_img:
                validate_image_file_extension(id_img)
                max_size = getattr(settings, 'MAX_IMAGE_SIZE',1024*1024*5)
                if id_img.size > max_size:
                    return JsonResponse({'error':f'loo large img (max size:{max_size})'})
                try:
                    img = Image.open(id_img)
                    img.verify()
                except Exception:
                    return JsonResponse({'img_error':'invalid img'},status=409)
            else:
                return JsonResponse({'img_error':'no img'},status=409)
            

            try:
                register_request = StudentRegistretionRequest( 
                    faculty_name=faculty,
                    department_name=department,
                    first_name = first_name,
                    last_name = last_name,
                    username = username,
                    id_img = id_img,
                    email = email
                )
                register_request.set_passwd(passwd)
                register_request.save()

            except Exception:
                return JsonResponse({'error':'incorrect info'},status=409)   
                         
            return render(request,"Users/register_sucsessfull.html")

        elif role == "staff":
            fullname = request.POST.get('staffName')
            staff_type = request.POST.get('staffType')

            try:
                register_request = StaffRegistretionRequest(
                    faculty_name=faculty,
                    department_name=department,
                    fullname= fullname,
                    staff_type=staff_type,
                    email = email,
                    username = username
                )
                register_request.set_passwd(passwd)
                register_request.save()

            except Exception as e:
                return JsonResponse({'error':'incorrect info'},status=409)
            
            return render(request,"Users/register_sucsessfull.html")
        else:
            return HttpResponse("someting went wrong!")

    
    return render(request,"Users/register.html",{'faculties':faculties,'departments':departments})
