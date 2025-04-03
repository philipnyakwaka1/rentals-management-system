from django.urls import path
from . import views
from buildings.api.v1 import views as building_api

urlpatterns = [
    path('',views.home_template, name="home-page"),
    path('buildings', views.buildings_template,name="buildings"),
]