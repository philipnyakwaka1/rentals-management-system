from django.urls import path
from buildings.api.v1 import views as building_api

urlpatterns = [
    path('', building_api.create_query_buildings, name="api-create_query_building"),
    path('<int:building_id>', building_api.get_update_building_api, name='api-get_update_building'),
    path('<int:building_id>/profile', building_api.add_building_profile, name='api-add_building_profile'),
    path('<int:building_id>/profile/<int:user_id>', building_api.delete_building_profile, name='api-delete_building_profile'),
    path('<int:building_id>/users', building_api.building_users, name="api-building_users"),
    path('by-user/<int:user_id>', building_api.user_buildings, name='api-buildings_by_user')
]