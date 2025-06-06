from django.urls import path
from buildings.api.v1 import views as building_api

urlpatterns = [
    path('', building_api.building_list_create, name="api-building_list_create"),
    path('<int:building_id>/', building_api.building_retrieve_update, name='api-building_retrieve_update'),
    #path('<int:building_id>/profile/', building_api.building_profile_add, name='api-building_profile_add'),
    #path('<int:building_id>/profile/<int:user_id>/', building_api.building_profile_delete, name='api-building_profile_delete'),
    #path('<int:building_id>/users', building_api.building_users, name="api-building_users_list"),
    path('by-user/<int:user_id>/', building_api.buildings_list_by_user, name='api-buildings_list_by_user')
]