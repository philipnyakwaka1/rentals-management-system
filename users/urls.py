from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_user, name="user-login"),
    path('logout', views.logout_user, name="user-logout"),
    path('register', views.register_user, name="user-register"),
    path('', views.home_page, name="home-page")
]
