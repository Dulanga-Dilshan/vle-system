from django.urls import path
from . import views

urlpatterns = [
    path('',views.test_api),
    path('faculties/create/',views.create_faculty),
    path('faculties/<int:id>/delete/',views.delete_faculty),
    path('faculties/<int:id>/update/',views.update_faculty),

    path('departments/create/',views.create_department),
    path('departments/<int:id>/update/',views.update_department),
    path('departments/<int:id>/delete/',views.delete_department),

    path('batches/create/',views.create_batch),
    path('batches/<int:id>/update/',views.update_batch),
    path('batches/<int:id>/delete/',views.delete_batch),
    path('batches/<int:id>/add_students/',views.add_students_to_batch),
    path('batches/<int:id>/remove_student/',views.remove_student_from_batch),
    path('batches/<int:id>/register-new-students/',views.register_new_students),

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

]
