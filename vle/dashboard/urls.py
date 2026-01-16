from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views,annosments
from university import views as university_views



app_name= 'dashboard'

urlpatterns = [
    path('',views.route,name='route'),

    path('student/',views.student,name='student'),
    path('staff/',views.staff,name='staff'),

    path('admin/',views.admin,name='admin'),
    path('admin/manage_requests/',views.manage_register_requests,name='manage_requests'),
    path('admin/manage_student_requests/',views.manage_student_register_requests,name='manage_student_requests'),
    path('admin/manage_staff_requests/',views.manage_staff_register_requests,name='manage_staff_requests'),
    path('admin/manage_users/',views.manage_users,name='manage_users'),
    path('admin/manage_courses/',views.manage_courses,name='manage_courses'),
    path('admin/manage_courses/<int:id>/',university_views.manage_course,name='manage_course'),
    path('admin/delete_subject/<int:id>/',university_views.delete_subject,name='delete_subject'),
    path('admin/add_subject/',university_views.add_subject,name='add_subject'),
    path('admin/add_semester/',university_views.add_semester,name='add_semester'),
    path('admin/update_subject/',university_views.update_subject,name='update_subject'),
    path('admin/post_annousment/',annosments.post_annousment,name='post_annousment'),
    path('admin/delete_announcement/<int:id>/',annosments.delete_announcement,name='delete_annousment'),
    path('admin/system_stats/',views.system_state,name='system_state'),
    path('admin/system_settings/',views.system_settings,name='system_settings'),
    path('admin/manage_faculties/',university_views.manage_faculties,name='manage_faculties'),
    path('admin/manage_faculty/<int:id>/',university_views.manage_faculty,name='manage_faculty'),
    path('admin/manage_batches/',university_views.manage_batches,name='manage_batches'),
    path('admin/manage_batch/<int:id>/',university_views.manage_batch,name='manage_batch'),

    
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
