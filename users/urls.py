from django.urls import path
from . import views

urlpatterns = [
    path('', views.users_home_page, name='users-home')
]