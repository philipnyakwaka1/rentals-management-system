from django.urls import path
from . import views
from .api.v1 import views as _api_views

urlpatterns = [
    path('', views.users_home_page, name='users-home'),
    path('register', _api_views.register_user_api, name='users-register-api'),
    path('profile', _api_views.update_user_profile_api, name='profile-update-api'),
]