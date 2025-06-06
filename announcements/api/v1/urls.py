from django.urls import path
from . import views

urlpatterns = [
    path('comments/', views.comment_list_create, name='api_comment_list_create'),
    path('comments/by-user/<int:user_id>/', views.comment_list_by_user, name='api_comment_list_by_user'),
    path('comments/by-building/<int:building_id>/', views.comment_list_by_building, name='api_comment_list_by_building'),
    path('comments/<int:comment_id>/', views.comment_retrieve_update, name='api_comment_retrieve_update'),
    path('notices/', views.notice_list_create, name='api_notice_list_create'),
    path('notices/by-user/<int:user_id>/', views.notice_list_by_user, name='api_notice_list_by_user'),
    path('notices/by-building/<int:building_id>/', views.notice_list_by_building, name='api_notice_list_by_building'),
    path('notices/<int:notice_id>/', views.notice_retrieve_update, name='api_notice_retrieve_update'),
]