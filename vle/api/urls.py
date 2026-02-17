from django.urls import path
from . import views

app_name= 'api'

from rest_framework import response,status
from rest_framework.decorators import api_view

@api_view(['GET'])
def test(request):
    return response.Response({str(urlpatterns)},status=status.HTTP_200_OK)

urlpatterns = [
    path('',test),
    path('faculties/create/',views.create_faculty),          
    path('faculties/<int:id>/delete/',views.delete_faculty), 
    path('faculties/<int:id>/update/',views.update_faculty),
    path('faculty/<int:faculty_id>/resources/add/',views.add_resource), 
    path('faculty/<int:faculty_id>/resources/<int:resource_id>/update/',views.update_resource),
    path('faculty/<int:faculty_id>/resources/<int:resource_id>/delete/',views.delete_resource),

    path('departments/create/',views.create_department),        
    path('departments/<int:id>/update/',views.update_department), 
    path('departments/<int:id>/delete/',views.delete_department), 

    path('batches/create/',views.create_batch),
    path('batches/<int:id>/update/',views.update_batch),
    path('batches/<int:id>/delete/',views.delete_batch),
    path('batches/<int:id>/add_students/',views.add_students_to_batch),
    path('batches/<int:id>/remove_student/',views.remove_student_from_batch),
    path('batches/<int:id>/register-new-students/',views.register_new_students),
    path('<int:batch_id>/batch-subjects/',views.get_batch_subjects),
    path('assign-lecture/',views.assign_lecture),
    path('batches/<int:batch_id>/advance-batch/',views.advance_batch),


    path('create_user/student/',views.create_user_student),
    path('create_user/staff/',views.create_user_staff),
    path('toggle_user_status/',views.set_user_state),
    path('bulk_user_status/',views.bulk_user_status),
    path('reset_password/',views.rest_user_psswd),
    path('delete_user/',views.delete_user),
    path('bulk_delete_users/',views.bulk_delete_users),
    path('update_user/',views.update_user),
    path('update_user_field/',views.update_user_field),
    path('update_user_faculty_department/',views.update_user_field),

    path('get-setting/<str:key>/',views.get_settings),
    path('get-all-setting/',views.get_all_settings),
    path('update-setting/',views.update_settings),

    path('get-stats/',views.get_stats),

    path('mark_annoucments/',views.mark_annoucments),
    path('remove_annoucments/',views.remove_annoucments),

    path('timetable/<int:batch_id>/',views.get_schedules),
    path('time-table/<int:batch_id>/available-halls/',views.availble_halls),
    path('schedules/create/',views.create_schedule),
    path('schedules/<int:schedule_id>/update/',views.update_shedule),
    path('schedules/<int:schedule_id>/delete/',views.delete_shedule),



]

