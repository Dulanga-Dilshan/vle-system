from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,Http404
from django.shortcuts import render,redirect,get_object_or_404
from university.models import Faculty
from Users.models import Staff
from  .models import Announcement,UserAnnouncement
from Users.models import User
from django.core.exceptions import PermissionDenied
from dashboard.recent_activity import log_activity




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
        if Announcement.objects.filter().first().title != request.POST.get('title'):
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
    

    log_activity(actor=request.user,action=f"Annousment '{announcement.title}' Deleted.")
    announcement.delete()
    return HttpResponse('announcement deleted',status=200)


def get_announcements(user:User)->dict:
    announcements = Announcement.objects.all()
    user_annousments = UserAnnouncement.objects.filter(user=user)
    
    _announcements = {
        'annoucements_unread':[],
        'annoucements_read':[],
    }

    isread = False
    isremoved = False

    for annousment in announcements:
        if annousment.is_targeted(user=user):
            if user_annousments:
                for user_annousment in user_annousments:
                    if annousment.id == user_annousment.announcement.id:
                        isread = True
                        if user_annousment.removed:
                            isremoved = True

                        break
                
                if isread and not isremoved:
                    _announcements['annoucements_read'].append(annousment)
                
                if not isread and not isremoved:
                    _announcements['annoucements_unread'].append(annousment)
                
                isremoved = isread = False

            else:
                _announcements['annoucements_unread'].append(annousment)

    
    return _announcements


def mark_annoucements(user:User,annousment_id:int,as_delete:bool=False):
    announcement = Announcement.objects.filter(id=annousment_id).first()
    if not announcement:
        raise Http404('no annousment')
    if not announcement.is_targeted(user):
        raise PermissionDenied('no permissions')
    
    if UserAnnouncement.objects.filter(user=user,announcement=announcement).exists():
        if as_delete:
            user_annousement = UserAnnouncement.objects.filter(user=user,announcement=announcement).first()
            user_annousement.removed = True
            user_annousement.save()
            return
    
    recode,created=UserAnnouncement.objects.get_or_create(user=user,announcement=announcement)

    if created:
        if as_delete:
            recode.removed=True
            recode.save()
