from django.urls import path
from . import views

urlpatterns = [
    path('comment', views.create_get_comment_api, name="api-create_get_comment"),
    path('comment/<int:comment_pk>', views.get_update_comment_api, name="api-get_update_comment"),
    path('notice', views.create_get_notice_api, name="api-cteate_get_notice"),
    path('notice/<int:notice_pk>', views.get_update_notice_api, name="api-get_update_notice"),
    path('comment', views.user_comments, name='api-get_user_comments'),
    path('notice', views.user_notices, name='api-get-user_notices'),
]