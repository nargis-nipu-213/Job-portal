
from django.db import models
from accounts.models import User

class Job(models.Model):
    recruiter=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    description=models.TextField()
    skills=models.TextField()
    openings=models.IntegerField()
    company_logo=models.ImageField(upload_to='company_logos/', null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-created_at']


class JobApplication(models.Model):
    job=models.ForeignKey(Job,on_delete=models.CASCADE)
    applicant=models.ForeignKey(User,on_delete=models.CASCADE)
    applied_on=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title}"

