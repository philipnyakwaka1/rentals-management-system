from django.urls import path
from . import views

urlpatterns = [
    path('', views.users_list, name='api-users_list'),
    path('register/', views.user_register, name='api-user_register'),
    path('login/', views.user_login, name='api-user_login'),
    path('logout/', views.user_logout, name='api-user_logout'),
    path('refresh_token/', views.refresh_tokens, name='refresh_token'),
    path('<int:user_id>/', views.user_retrieve_update, name='api-user_retrieve_update'),
    path('profile/<int:user_id>/', views.profile_retrieve_update, name='api-profile_retrieve_update'),
    path('by-building/<int:building_id>', views.users_list_by_building, name="api-users_list_by_building"),
    path('building/<int:building_id>/profile/add/', views.add_profile_to_building, name='api-profile_add_to_building'),
    path('building/<int:building_id>/profile/<int:user_id>/remove/', views.remove_profile_from_building, name='api-profile_remove_from_building'),
]