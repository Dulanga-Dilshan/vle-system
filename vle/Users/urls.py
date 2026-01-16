from django.urls import path
from . import views


app_name= 'Users'

urlpatterns = [
    path('',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('register/',views.register_user,name='register'),
    path('test/',views.test,name='test'),
]