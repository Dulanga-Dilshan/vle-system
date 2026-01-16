from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from university.models import Faculty
from Users.models import Staff
from  .models import Announcement
import json



@login_required(login_url='Users:login')
def post_annousment(request):
    context = {}

    if request.user.is_staff == 0:
        return redirect('dashboard:route')
    
    if request.user.role == 'staff':
        context['faculties'] = [Staff.objects.get(username=request.user).faculty_name]
    else:
        context['faculties']=Faculty.objects.all()

    context['announcements'] = Announcement.objects.all()
    context['user'] = request.user
    
    if request.method=='POST':
        target_audience_rule = {}
        audience_type = request.POST.get('audience_type')
        if audience_type == 'all':
            target_audience_rule['audience_type']='all'
        else:
            group = request.POST.get('group')
            target_audience_rule['audience_type']=group
            if group == 'students':
                target_audience_rule['group'] = { 'year':request.POST.get('student_year'),'faculty':request.POST.get('student_faculty') }
    
            elif group == 'staff':
                target_audience_rule['group'] = { 'type':request.POST.get('staff_type'),'faculty':request.POST.get('staff_faculty') }
            
            elif group == 'faculty':
                target_audience_rule['group'] = { 'faculty':request.POST.get('faculty') }


        new_annousment=Announcement(
            title = request.POST.get('title'),
            announcement = request.POST.get('message'),
            target_audience_rule = target_audience_rule,
            created_by = request.user
        )

        try:
            new_annousment.save()
        except Exception as e:
            print(e)
        
    return render(request,'dashboard/admin/anousment.html',context)


@login_required(login_url='Users:login')
def delete_announcement(request,id:int)->HttpResponse:
    if request.user.is_staff == 0:
        return HttpResponse('bad request(no permissions)',status=400)

    announcement = get_object_or_404(Announcement,id=id)

    if request.user.role == 'staff':
        if request.user != announcement.created_by:
            return HttpResponse('bad request(no permissions)',status=400)
        
    announcement.delete()

    return HttpResponse('announcement deleted',status=200)



