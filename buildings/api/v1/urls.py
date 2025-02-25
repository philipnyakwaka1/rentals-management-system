from django.urls import path
from buildings.api.v1 import views as building_api

urlpatterns = [
    path('', building_api.create_query_buildings, name="api-create_query_buildings"),
    path('<int:building_pk>', building_api.get_update_building_api, name='api-get_update_building'),
    path('<int:building_pk>/users', building_api.user_buildings, name="api-get_user_buildings"),
    path('<int:building_pk>/comments', building_api.building_comments, name="api-get_user_buildings"),
    path('<int:building_pk>/notices', building_api.building_notices, name="api-get_user_buildings"),
]