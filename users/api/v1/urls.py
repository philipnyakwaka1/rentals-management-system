from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_users_api, name='api-get_users'),
    path('<int:user_pk>', views.get_update_user_api, name='api-update_user'),
    path('<int:user_pk>/buildings', views.user_buildings, name='api-user_buildings'),
    path('register', views.register_user_api, name='api-register_users'),
    path('profile/<int:user_pk>', views.get_update_profile_api, name='api-get_update_profile'),
]