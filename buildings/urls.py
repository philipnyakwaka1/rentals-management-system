from django.urls import path
from . import views

#urlpatterns should be the variable name, it is a sequence of path()
urlpatterns = [
    path('hello_world', views.hello_world, name='buildings-hello_world'),
]