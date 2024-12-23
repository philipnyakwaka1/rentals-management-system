from django.shortcuts import render
from django.http import HttpResponse

def users_home_page(request):
    return HttpResponse('users home page')
