from django.urls import path
from . import views

urlpatterns = [
    path('', views.announcements_page, name='announcements-home')
]