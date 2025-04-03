from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_users_api, name='api-get_users'),
    path('login', views.JWT_login_view, name='JWT-login_view'),
    path('<int:user_pk>', views.get_update_user_api, name='api-update_user'),
    path('<int:user_pk>/buildings', views.user_buildings, name='api-user_buildings'),
    path('register', views.register_user_api, name='api-register_users'),
    path('profile/<int:user_pk>', views.get_update_profile_api, name='api-get_update_profile'),
]