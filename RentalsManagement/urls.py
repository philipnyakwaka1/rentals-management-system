"""
URL configuration for RentalsManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import os
from dotenv import load_dotenv

load_dotenv()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('users.urls')),
    path('api/v1/users/', include('users.api.v1.urls')),
    path('announcements/', include('announcements.urls')),
    path('api/v1/announcements/', include('announcements.api.v1.urls')),
    path('api/v1/building/', include('buildings.api.v1.urls')),
    path('buildings/', include('buildings.urls')),
]

# Conditionally add portfolio URLs (not tracked in git)
if os.getenv('ENABLE_PORTFOLIO_APP', 'false').lower() == 'true':
    urlpatterns.insert(1, path('', include('portfolio.urls')))
