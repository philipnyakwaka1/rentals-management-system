from django.urls import path
from . import views

urlpatterns = [
    path('comments/', views.create_get_comment_api, name='api_comment_list_create'),
    path('comments/by-user/<int:user_id>', views.user_comments, name='api_comment_list_by_user'),
    path('comments/by-building/<int:building_id>', views.building_comments, name='api_comment_list_by_building'),
    path('comments/<int:comment_id>', views.get_update_comment_api, name='api_comment_retrieve_update'),
    path('notices/', views.create_get_notice_api, name='api_notice_list_create'),
    path('notices/by-user/<int:user_id>', views.user_notices, name='api_notice_list_by_user'),
    path('notices/by-building/<int:building_id>', views.building_notices, name='api_notice_list_by_building'),
    path('notices/<int:notice_id>', views.get_update_notice_api, name='api_notice_retrieve_update'),
]