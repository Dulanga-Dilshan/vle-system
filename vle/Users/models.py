from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from university.models import Faculty,Department,Batch
from django.contrib.auth.hashers import make_password

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")

        extra_fields.setdefault('role', User.Roles.STUDENT)

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields['role'] = User.Roles.ADMIN

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT = "student"
        STAFF = "staff"
        ADMIN = "admin"

    role = models.CharField(max_length=20, choices=Roles.choices, default='student')
    last_activity = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    def __str__(self):
        return super().__str__()
    
class Staff(models.Model):
    class stf_type(models.TextChoices):
        lecture = 'lecture'
        profesor = 'profesor'
        admin = 'admin'
        support = 'support'

    name = models.CharField(max_length=30)
    faculty_name = models.ForeignKey(Faculty,on_delete=models.CASCADE, null=True)
    department_name = models.ForeignKey(Department,on_delete=models.CASCADE, null=True)
    username = models.OneToOneField(User,on_delete=models.CASCADE, null=True)
    staff_type = models.CharField(max_length=20,choices=stf_type.choices, default='lecture')

    def __str__(self):
        return self.name
    
class Student(models.Model):
    name = models.CharField(max_length=20)
    faculty_name = models.ForeignKey(Faculty,on_delete=models.CASCADE, null=True)
    department_name = models.ForeignKey(Department,on_delete=models.CASCADE, null=True)
    username = models.OneToOneField(User,on_delete=models.CASCADE, null=True)
    batch = models.ForeignKey(Batch,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return self.name


class StudentRegistretionRequest(models.Model):
    faculty_name = models.ForeignKey(Faculty,on_delete=models.CASCADE, null=True)
    department_name = models.ForeignKey(Department,on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    username = models.CharField(max_length=20,unique=True)
    id_img = models.ImageField(upload_to='student_ids/',null=True,blank=True)
    email = models.EmailField(max_length=50,unique=True)
    date = models.DateField(auto_now_add=True,null=True)
    passwd_hash = models.CharField(max_length=128)

    def set_passwd(self,row_passwd):
        self.passwd_hash=make_password(row_passwd)

    def __str__(self):
        return f"{self.first_name} - {self.username}"

class StaffRegistretionRequest(models.Model):
    class stf_type(models.TextChoices):
        lecture = 'lecture'
        profesor = 'profesor'
        admin = 'admin'
        support = 'support'
    
    faculty_name = models.ForeignKey(Faculty,on_delete=models.CASCADE, null=True)
    department_name = models.ForeignKey(Department,on_delete=models.CASCADE, null=True)
    staff_type = models.CharField(max_length=20,choices=stf_type.choices, default='lecture')
    fullname = models.CharField(max_length=50)
    username = models.CharField(max_length=20,unique=True)
    email = models.EmailField(max_length=50,unique=True)
    date = models.DateField(auto_now_add=True,null=True)
    passwd_hash = models.CharField(max_length=128)

    def set_passwd(self,row_passwd):
        self.passwd_hash=make_password(row_passwd)

    def __str__(self):
        return f"{self.fullname} - {self.username}"
    