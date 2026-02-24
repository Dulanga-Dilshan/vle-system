from django.db import models,transaction
from pymediainfo import MediaInfo
from django.core.exceptions import ValidationError
from config.config import get_setting


semesters = [1.1,1.2,2.1,2.2,3.1,3.2,4.1,4.2]

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
    
class LectureHall(models.Model):
    HALL_TYPE = [
        ('LAB', 'Laboratory'),
        ('LH', 'Lecture Hall'),
        ('SEMINAR', 'Seminar Room'),
        ('AUD', 'Auditorium'),
        ('CONF', 'Conference Hall'),
    ]

    faculty = models.ForeignKey(Faculty,on_delete=models.CASCADE)
    name = models.CharField(max_length=50,unique=True)
    hall_type = models.CharField(max_length=10,choices=HALL_TYPE,default='LH')
    capacity = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.hall_type}"

    
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
    number = models.DecimalField(max_digits=2,decimal_places=1,default=1.1)
    
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
    
   
class Schedule(models.Model):
    DAYS = [
        ('mon','monday'),
        ('tue','tuesday'),
        ('wed','wednesday'),
        ('thu','thursday'),
        ('fri','friday'),
    ]

    subject = models.ForeignKey(BatchSubject,on_delete=models.CASCADE)
    hall = models.ForeignKey(LectureHall,on_delete=models.CASCADE)
    substitute_teacher = models.ForeignKey("Users.Staff",on_delete=models.SET_NULL,null=True,blank=True)
    day = models.CharField(choices=DAYS,max_length=5,default='mon')
    start_time = models.CharField(max_length=10)
    end_time = models.CharField(max_length=10)
    notes = models.TextField(max_length=100,null=True,blank=True,default='')

    class Meta:
        ordering = ['day','start_time']

    def __str__(self):
        return f'{self.subject.subject.code} - {self.day}'


class  LectureMaterials(models.Model):
    MATERIAL_TYPES = [
        ('pdf','PDF'),
        ('vid','Video'),
        ('link','Link'),
        ('doc','Document')
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    material_type = models.CharField(choices=MATERIAL_TYPES,max_length=10,default='pdf')
    subject = models.ForeignKey(BatchSubject,on_delete=models.CASCADE)
    file = models.FileField(upload_to='lecture_materials/',null=True,blank=True)
    external_url = models.URLField(null=True, blank=True)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    file_detail = models.CharField(max_length=300,null=True,blank=True)
    file_size = models.BigIntegerField(null=True, blank=True) #bytes

    class Meta:
        ordering = ['uploaded_on']
    
    def __str__(self):
        return f"{self.subject.subject.code} - {self.material_type}"
    
    def _get_detail(self):
        if self.material_type == 'pdf' or self.material_type == 'doc' :
            if self.file:
                if self.file.size < 1024:
                    return f"{self.file.size} Bytes"
                if self.file.size<(1024*1024): #kB
                    return f"{self.file.size/1024:.2f}kB"
                return f"{self.file.size/(1024*1024):.2f}MB"
        
            else:
                return None
        
        if self.material_type == 'link':
            if self.external_url:
                return self.external_url
            
            return None

        if self.material_type == 'vid':
            duration = None
            if self.file:
                media = MediaInfo.parse(self.file.path)
                for track in media.tracks:
                    if track.track_type == "Video":
                        duration = float(track.duration) / 1000
                        break
                
                for track in media.tracks:
                    if track.track_type == "General" and track.duration:
                        duration = float(track.duration) / 1000.0

                if duration:
                    return f"{int(duration//60)}:{int(duration%60):02d}"
                else:
                    return None
        
        return None
            
    def clean(self):
        super().clean()
        if self.material_type == 'link':
            if self.external_url is None:
                raise ValidationError({"external_url": "Link type requires a URL."})
            return
        
        if self.file is None:
            raise ValidationError({"file": "This material type requires an uploaded file."})
        
        if self.file.size > get_setting('MAX_UPLOAD_MB')*1024*1024:
            raise ValidationError({"file": "File too large. Max is 100MB."})
        
        qs = LectureMaterials.objects.filter(subject=self.subject).exclude(pk=self.pk)
        used = qs.aggregate(total=models.Sum("file_size"))["total"] or 0

        if used + self.file.size > (get_setting('MAX_UPLOAD_PER_COURSE_MB')*1024*1024):#bytes
            raise ValidationError({"file": f"Subject storage limit exceeded (max {get_setting('MAX_UPLOAD_PER_COURSE_MB')}MB per subject)."})
        

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.file_detail = self._get_detail()
        file_size = None
        if self.material_type != 'link' and self.file:
            self.file_size = self.file.size

        super().save(update_fields=['file_detail','file_size'])



        

        
                