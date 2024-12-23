from django.shortcuts import render
from django.http import HttpResponse

def announcements_page(request):
    return HttpResponse('Announcements')
