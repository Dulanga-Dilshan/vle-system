from django.db import models


# Create your models here.
class University(models.Model):
    name = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.name
    
class Faculty(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    code = models.CharField(max_length=30,null=True)
    name = models.CharField(max_length=50,unique=True)
    dean = models.ForeignKey("Users.Staff", on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ('university','name')
    
    def __str__(self):
        return self.name


class Department(models.Model):
    faculty= models.ForeignKey(Faculty, on_delete=models.CASCADE)
    name= models.CharField(max_length=50,unique=True)
    code = models.CharField(max_length=30,null=True)
    head= models.ForeignKey("Users.Staff", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('faculty','name')
    
    def __str__(self):
        return f"{self.name} - {self.faculty.name }"
    
class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE,related_name='courses')
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    duration_years = models.PositiveSmallIntegerField()
    description = models.CharField(max_length=100,null=True)
    
    def __str__(self):
        return self.name
    
class Batch(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE, related_name='batches')
    progression_year = models.DecimalField(max_digits=2,decimal_places=1,default=1.1)
    intake_year = models.PositiveIntegerField(null=True)
    name = models.CharField(max_length=50,null=True)
    is_active =models.BooleanField(null=True)

    class Meta:
        unique_together = ('course' , 'intake_year')
        
    def __str__(self):
        return self.name


class Semester(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='semesters')
    number = models.PositiveSmallIntegerField()
    
    class Meta:
        unique_together = ('course' , 'number')
    
    def __str__(self):
        return f'{self.course.code} - {self.number}'
    

class Subject(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE,related_name='subjects')
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='subjects')
    semester = models.ForeignKey(Semester,on_delete=models.CASCADE,related_name='subjects')
    code = models.CharField(max_length=30,unique=True)
    name = models.CharField(max_length=40)
    credits = models.PositiveSmallIntegerField()
    total_hours = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('code' , 'course')
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class BatchSubject(models.Model):
    batch = models.ForeignKey(Batch,on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    staff = models.ForeignKey("Users.Staff",on_delete=models.SET_NULL,null=True,blank=True)

    class Meta:
        unique_together = ('batch' , 'subject')

    def __str__(self):
        return f"{self.batch} - {self.subject}"