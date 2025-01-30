from django.urls import path
from . import views
from announcements.api.v1 import views as announcement_api

urlpatterns = [
    path('comment', announcement_api.create_get_comment_api, name="api-create_get_comment"),
    path('comment/<int:comment_pk>', announcement_api.get_update_comment_api, name="api-get_update_comment"),
    path('notice', announcement_api.create_get_notice_api, name="api-cteate_get_notice"),
    path('notice/<int:notice_id>', announcement_api.get_update_notice_api, name="api-get_update_notice"),
    path('comment', announcement_api.user_comments, name='api-get_user_comments'),
    path('notice', announcement_api.user_notices, name='api-get-user_notices'),
]
