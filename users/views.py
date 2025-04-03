from django.shortcuts import render

def home_page(request):
    return render(request, 'users/practice.html')


def register_user(request):
    return render(request, 'users/register.html')

def login_user(request):
    return render(request, 'users/login.html')

def logout_user(request):
    return render(request, 'users/logout.html')