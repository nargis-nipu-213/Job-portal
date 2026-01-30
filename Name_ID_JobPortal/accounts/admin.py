from django.contrib import admin
from .models import User, RecruiterProfile, JobSeekerProfile

admin.site.register(User)
admin.site.register(RecruiterProfile)
admin.site.register(JobSeekerProfile)