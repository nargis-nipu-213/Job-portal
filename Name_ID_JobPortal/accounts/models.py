
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE=(('RECRUITER','Recruiter'),('JOBSEEKER','Jobseeker'))
    user_type=models.CharField(max_length=20,choices=USER_TYPE)

class RecruiterProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    company_name=models.CharField(max_length=200)
    company_description=models.TextField()

class JobSeekerProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    skills=models.TextField()
    resume=models.FileField(upload_to='resumes/')
