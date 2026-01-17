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


]
