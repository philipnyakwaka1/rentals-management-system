from django.shortcuts import render
from django.http import HttpResponse

def home_page(request):
    return HttpResponse('Home Page')
