from django.urls import path
from buildings.api.v1 import views as building_api

urlpatterns = [
    path('', building_api.create_query_buildings, name="api-create_query_building"),
    path('<int:building_pk>', building_api.get_update_building_api, name='api-get_update_building'),
    path('<int:building_pk>/profile', building_api.add_building_profile, name='api-add_building_profile'),
    path('<int:building_pk>/profile/<int:user_id>', building_api.delete_building_profile, name='api-delete_building_profile'),
    path('<int:building_pk>/users', building_api.building_users, name="api-building_users"),
    path('<int:building_pk>/comments', building_api.building_comments, name="api-building_comments"),
    path('<int:building_pk>/notices', building_api.building_notices, name="api-building_notices"),
]