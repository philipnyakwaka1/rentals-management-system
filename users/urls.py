from django.urls import path
from . import views
from .api.v1 import views as user_api

urlpatterns = [
    path('', user_api.get_users_api, name='api-get_users'),
    path('<int:user_pk>', user_api.get_update_user_api, name='api-update_user'),
    path('register', user_api.register_user_api, name='api-register_users'),
    path('profile/<int:user_pk>', user_api.get_update_profile_api, name='api-get_update_profile'),
]
