from django.urls import path
from . import views

urlpatterns = [
    path('comments', views.create_get_comment_api, name="api-create_get_comment"),
    path('comments/<int:comment_pk>', views.get_update_comment_api, name="api-get_update_comment"),
    path('notices', views.create_get_notice_api, name="api-create_get_notice"),
    path('notices/<int:notice_pk>', views.get_update_notice_api, name="api-get_update_notice"),
]