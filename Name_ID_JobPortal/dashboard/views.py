
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from jobs.models import Job, JobApplication

def home(request):
    """Home page - shows available jobs with search for all users"""
    q = request.GET.get('q', '').strip()
    jobs = Job.objects.all()
    matched_jobs = []
    show_skill_match = False
    
    if q:
        jobs = jobs.filter(title__icontains=q) | jobs.filter(skills__icontains=q) | jobs.filter(description__icontains=q)
    
    # Skill matching for authenticated jobseekers
    if request.user.is_authenticated and request.user.user_type == 'JOBSEEKER':
        show_skill_match = True
        try:
            user_skills = set(request.user.jobseekerprofile.skills.lower().split(','))
            user_skills = set([s.strip() for s in user_skills if s.strip()])
            for job in jobs:
                job_skills = set([s.strip().lower() for s in job.skills.split(',') if s.strip()])
                if user_skills & job_skills:
                    matched_jobs.append(job)
        except:
            matched_jobs = list(jobs)
    
    return render(request, 'home.html', {
        'jobs': jobs,
        'matched_jobs': matched_jobs,
        'query': q,
        'show_skill_match': show_skill_match
    })

@login_required
def dashboard(request):
    """Authenticated dashboard - role-based view"""
    matched = []
    your_jobs = []
    all_jobs = Job.objects.all()
    
    if request.user.user_type == 'JOBSEEKER':
        # Skill matching for jobseekers
        try:
            skills = set(request.user.jobseekerprofile.skills.lower().split(','))
            for job in all_jobs:
                job_skills = set(job.skills.lower().split(','))
                # Check if any skills match
                if skills & job_skills:
                    matched.append(job)
        except:
            pass
        
        # Get applied jobs
        applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_on')
        
        return render(request, 'dashboard.html', {
            'matched': matched,
            'applications': applications
        })
    elif request.user.user_type == 'RECRUITER':
        # Show recruiter's job postings
        your_jobs = Job.objects.filter(recruiter=request.user)
        return render(request, 'dashboard.html', {
            'your_jobs': your_jobs,
            'page_title': 'My Job Postings'
        })
    
    return render(request, 'dashboard.html', {'matched': matched, 'your_jobs': your_jobs})

