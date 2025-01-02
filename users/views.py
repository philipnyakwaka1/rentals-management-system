from django.shortcuts import render
from django.http import HttpResponse

def users_home_page(request):
    return HttpResponse('users home page')


def register_user(request):
    pass

def login_user(request):
    # get username and password from request.POST
    # check the password validy against the user's hashed password
    # authenticate / login user
    # return relevant json response with status code for api
    # redirect the authenticated user to home page
    pass

def logout_user(request):
    # get username from request.POST
    # logout the user and end the user session
    # return proper json response / redirect to login page
    pass