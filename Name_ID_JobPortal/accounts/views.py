
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .models import JobSeekerProfile,RecruiterProfile

def login_view(request):
    if request.method=='POST':
        u=request.POST['username']
        p=request.POST['password']
        user=authenticate(request,username=u,password=p)
        if user:
            login(request,user)
            messages.success(request,f'Welcome back, {user.first_name or user.username}!')
            return redirect('/')
        else:
            messages.error(request,'Invalid username or password.')
    return render(request,'accounts/login.html')

def register_view(request):
    if request.method=='POST':
        # basic validation
        pwd=request.POST.get('password')
        pwd2=request.POST.get('password2')
        username=request.POST.get('username','')
        email=request.POST.get('email','')
        if not pwd or pwd!=pwd2:
            messages.error(request,'Passwords do not match.')
            return render(request,'accounts/register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request,'Username already taken.')
            return render(request,'accounts/register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request,'Email already registered.')
            return render(request,'accounts/register.html')
        user=User.objects.create_user(
            username=username,
            password=pwd,
            user_type=request.POST['user_type'],
            email=email
        )
        # store display name into first_name for simplicity
        user.first_name=request.POST.get('display_name','')
        user.save()
        # create a blank profile depending on user type
        if user.user_type=='JOBSEEKER':
            JobSeekerProfile.objects.create(user=user,skills='')
        else:
            RecruiterProfile.objects.create(user=user,company_name='',company_description='')
        messages.success(request,'Account created! Please log in.')
        return redirect('/accounts/login/')
    return render(request,'accounts/register.html')


def logout_view(request):
    logout(request)
    messages.success(request,'Logged out successfully.')
    return redirect('/accounts/login/')


@login_required
def profile_view(request):
    # allow jobseeker to update skills and upload resume, recruiter updates company info
    user=request.user
    if user.user_type=='JOBSEEKER':
        profile=user.jobseekerprofile
        if request.method=='POST':
            profile.skills=request.POST.get('skills','')
            if request.FILES.get('resume'):
                profile.resume=request.FILES['resume']
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('/accounts/profile/')
        return render(request,'accounts/profile.html',{
            'profile': profile,
            'user': user
        })
    else:
        profile=user.recruiterprofile
        if request.method=='POST':
            profile.company_name=request.POST.get('company_name','')
            profile.company_description=request.POST.get('company_description','')
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('/accounts/profile/')
        return render(request,'accounts/profile.html',{
            'profile': profile,
            'user': user
        })
