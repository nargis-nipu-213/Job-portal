
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Job,JobApplication

def job_list(request):
    q=request.GET.get('q','').strip()
    view_type=request.GET.get('view','all')
    jobs=Job.objects.all()
    if q:
        jobs=jobs.filter(title__icontains=q) | jobs.filter(skills__icontains=q) | jobs.filter(description__icontains=q)
    
    # Skill match filter for jobseekers
    matched_jobs = []
    if view_type == 'matched' and request.user.is_authenticated and request.user.user_type == 'JOBSEEKER':
        try:
            user_skills = request.user.jobseekerprofile.skills.lower().split(',')
            user_skills = set([s.strip() for s in user_skills if s.strip()])
            for job in jobs:
                job_skills = set([s.strip().lower() for s in job.skills.split(',') if s.strip()])
                if user_skills & job_skills:
                    matched_jobs.append(job)
        except:
            matched_jobs = list(jobs)
    else:
        matched_jobs = list(jobs)
    
    return render(request,'jobs/list.html',{
        'jobs':matched_jobs,
        'query':q,
        'view_type':view_type,
        'show_skill_match': request.user.is_authenticated and request.user.user_type == 'JOBSEEKER'
    })


@login_required
def job_create(request):
    if request.user.user_type!='RECRUITER':
        messages.error(request,'Only recruiters can post jobs.')
        return redirect('/')
    if request.method=='POST':
        Job.objects.create(
            recruiter=request.user,
            title=request.POST.get('title',''),
            openings=int(request.POST.get('openings') or 1),
            description=request.POST.get('description',''),
            skills=request.POST.get('skills',''),
            company_logo=request.FILES.get('company_logo', None)
        )
        messages.success(request,'Job posted successfully!')
        return redirect('dashboard')
    return render(request,'jobs/create.html')


@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)
    if request.user.user_type != 'RECRUITER':
        messages.error(request, 'Only recruiters can edit jobs.')
        return redirect('/')
    if request.method == 'POST':
        job.title = request.POST.get('title', job.title)
        job.description = request.POST.get('description', job.description)
        job.skills = request.POST.get('skills', job.skills)
        job.openings = int(request.POST.get('openings') or job.openings)
        if request.FILES.get('company_logo'):
            job.company_logo = request.FILES['company_logo']
        job.save()
        messages.success(request, 'Job updated successfully!')
        return redirect('dashboard')
    return render(request, 'jobs/edit.html', {'job': job})


@login_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)
    if request.user.user_type != 'RECRUITER':
        messages.error(request, 'Only recruiters can delete jobs.')
        return redirect('/')
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('dashboard')
    return render(request, 'jobs/delete.html', {'job': job})


def job_detail(request,pk):
    job=get_object_or_404(Job,pk=pk)
    applied=False
    if request.user.is_authenticated:
        applied=JobApplication.objects.filter(job=job,applicant=request.user).exists()
    if request.method=='POST':
        if not request.user.is_authenticated or request.user.user_type!='JOBSEEKER':
            messages.error(request,'Only jobseekers can apply.')
            return redirect('/accounts/login/')
        if applied:
            messages.warning(request, 'You have already applied for this job!')
            return redirect('job_detail', pk=pk)
        # create application
        JobApplication.objects.create(job=job, applicant=request.user)
        messages.success(request,'Application submitted!')
        return redirect('dashboard')
    return render(request,'jobs/detail.html',{'job':job,'applied':applied})
