from rest_framework.test import APIClient, APITestCase
from buildings.api.v1 import views
from django.contrib.auth.models import User
from django.urls import reverse
import json
from announcements.models import Notice, Comment
from buildings.models import Building
from users.models import UserBuilding

class TestBuildings(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='Yyugbcdasdd@134')
        cls.tenant = User.objects.create_user(username='tenant', password='Gyuxxcdasdd@579')
        cls.regular_user = User.objects.create_user(username='regular_user', password='Gyuxxcdasdd@579')
        cls.regular_user_token = APIClient().post(reverse('JWT-login_view'), {'username': 'regular_user', 'password': 'Gyuxxcdasdd@579'}).json().get('access')
        cls.owner_token = APIClient().post(reverse('JWT-login_view'), {'username': 'owner', 'password': 'Yyugbcdasdd@134'}).json().get('access')
        cls.tenant_token = APIClient().post(reverse('JWT-login_view'), {'username': 'tenant', 'password': 'Gyuxxcdasdd@579'}).json().get('access')
        cls.admin = User.objects.create_superuser(username='admin_user', password="Yyugbcdasdd@134")
        cls.admin_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'admin_user', 'password': "Yyugbcdasdd@134"}).json()['access']
        cls.building_id = None
        cls.create_query_url = reverse('api-create_query_building')
    
    def setUp(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-4.0, 32.5',
        }
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.__class__.building_id = response.json().get('id')
        self.building = Building.objects.get(pk=self.building_id)
        self.tenant.profile.buildings.add(self.building, through_defaults={'relationship': 'tenant'})
    
    def get_update_building_url(self):
        if self.building_id is None:
            raise ValueError('building id not yet set')
        return reverse('api-get_update_building', args=[self.building_id])
    
    def get_building_profiles_url(self):
        if self.building_id is None:
            raise ValueError('building id not set')
        return reverse('api-building_users', args=[self.building_id])
    
    def add_building_profile_url(self):
        if self.building_id is None:
            raise ValueError('building id not set')
        return reverse('api-add_building_profile', args=[self.building_id])

    def delete_building_profile_url(self):
        if self.building_id is None:
            raise ValueError('building id not set')
        return reverse('api-delete_building_profile', args=[self.building_id, self.tenant.pk])
    
    def test_get_building_unauthenticated_user(self):
        response = self.client.get(self.get_update_building_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(json.loads(response.json())['features'][0]['properties']['pk']), self.building_id)
    
    def test_get_building_authenticated_user(self):
        response = self.client.get(self.get_update_building_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(json.loads(response.json())['features'][0]['properties']['pk']), self.building_id)
    
    def test_create_building_unauthenticated_user(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-4.0, 32.5',
        }
        response = self.client.put(self.create_query_url, data)
        self.assertEqual(response.status_code, 401)

    def test_create_building_invalid_coordinates(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-4.0 32.5',
        }
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('building')[0], 'Coordinate format cannot be parsed. The coordinate should be two floats values separated by a comma.')
        data['building'] = '-4.0, 2,4'
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('building')[0], 'Coordinate format cannot be parsed. The coordinate should be two floats values separated by a comma.')
        data['building'] = '-4.6g, 9'
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('building')[0], 'Coordinate format cannot be parsed. The coordinate should be two floats values separated by a comma.')
    
    def test_create_building_user_id_does_not_exist(self):
        data = {
            'user_id': self.owner.pk + self.admin.pk + self.tenant.pk + self.regular_user.pk,
            'building': '-3.0, 42.5',
        }
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'user does not exist')

    def test_create_building_user_profile_does_not_exists(self):
        self.owner.profile.delete()
        data = {
            'user_id': self.owner.pk ,
            'building': '-3.0, 42.5',
        }
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'user profile does not exist')

    def test_create_building_for_another_user_with_non_admin(self):
        data = {
            'user_id': self.regular_user.pk ,
            'building': '-3.0, 42.5',
        }
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to perform this action')

    def test_create_building_for_another_user_with_admin(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-4.0, 32.5',
        }
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 201)
        building_id = response.json().get('id')
        building = self.client.get(reverse('api-get_update_building', args=[building_id]))
        self.assertEqual(building.status_code, 200)
        self.assertEqual(int(json.loads(building.json())['features'][0]['properties']['pk']), building_id)

    def test_create_building_with_authenticated_user_and_query_all_buildings(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-3.0, 42.5',
        }
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 201)
        building_id = response.json().get('id')
        building = self.client.get(reverse('api-get_update_building', args=[building_id]))
        self.assertEqual(building.status_code, 200)
        self.assertEqual(int(json.loads(building.json())['features'][0]['properties']['pk']), building_id)
        all_buildings = self.client.get(self.create_query_url)
        self.assertEqual(all_buildings.status_code, 200)
        self.assertEqual(len(all_buildings.json().get('results')), 2)
    
    def test_update_building_unauthenticated_user(self):
        response = self.client.patch(self.get_update_building_url(), data={'building': '5.3, 42.1'})
        self.assertEqual(response.status_code, 401)
    
    def test_update_building_user_not_linked_to_building(self):
        response = self.client.patch(self.get_update_building_url(), data={'building': '5.3, 42.1', 'rent': 800}, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile is not linked to the building')
    
    def test_update_building_user_not_owner(self):
        response = self.client.patch(self.get_update_building_url(), data={'building': '5.3, 42.1', 'rent': 800}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building')
    
    def test_update_building_user_not_owner_but_is_admin(self):
        response = self.client.patch(self.get_update_building_url(), data={'building': '5.3, 42.1', 'rent': 800}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        building = json.loads(self.client.get(self.get_update_building_url()).json())
        self.assertEqual(building['features'][0]['geometry']['coordinates'][0], 42.1)
        self.assertEqual(building['features'][0]['geometry']['coordinates'][1], 5.3)
    
    def test_update_building_authenticated_owner(self):
        response = self.client.patch(self.get_update_building_url(), data={'building': '5.3, 42.1'},headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        building = json.loads(self.client.get(self.get_update_building_url(), data={'geojson': 'true'}).json())
        self.assertEqual(building['features'][0]['geometry']['coordinates'][0], 42.1)
        self.assertEqual(building['features'][0]['geometry']['coordinates'][1], 5.3)

    def test_get_building_users_unauthenticated(self):
        response = self.client.get(self.get_building_profiles_url())
        self.assertEqual(response.status_code, 401)

    def test_get_all_building_users_not_linked_to_building(self):
        response = self.client.get(self.get_building_profiles_url(), headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile not linked to building')

    def test_get_all_building_users_admin(self):
        response = self.client.get(self.get_building_profiles_url(), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 2)
        user_ids = list(map(lambda x: x['user']['id'], response.json()['results']))
        self.assertTrue(self.owner.pk in user_ids)
        self.assertTrue(self.tenant.pk in user_ids)
    
    def test_get_all_building_users_tenant(self):
        response = self.client.get(self.get_building_profiles_url(), headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 2)
        user_ids = list(map(lambda x: x['user']['id'], response.json()['results']))
        self.assertTrue(self.owner.pk in user_ids)
        self.assertTrue(self.tenant.pk in user_ids)
    
    def test_get_all_building_users_owner(self):
        response = self.client.get(self.get_building_profiles_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 2)
        user_ids = list(map(lambda x: x['user']['id'], response.json()['results']))
        self.assertTrue(self.owner.pk in user_ids)
        self.assertTrue(self.tenant.pk in user_ids)

    def test_get_building_tenants_user_not_linked_to_building(self):
        response = self.client.get(self.get_building_profiles_url(), data={'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile not linked to building')

    def test_get_building_owners_user_not_linked_to_building(self):
        response = self.client.get(self.get_building_profiles_url(), data={'relationship': 'owner'}, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile not linked to building')

    def test_get_building_tenants_user_linked_to_building(self):
        response = self.client.get(self.get_building_profiles_url(), data={'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.tenant.pk)
        response = self.client.get(self.get_building_profiles_url(), data={'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.tenant.pk)
        response = self.client.get(self.get_building_profiles_url(), data={'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.tenant.pk)

    def test_get_building_owners_user_linked_to_building(self):
        response = self.client.get(self.get_building_profiles_url(), data={'relationship': 'owner'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.owner.pk)
        response = self.client.get(self.get_building_profiles_url(), data={'relationship': 'owner'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.owner.pk)
        response = self.client.get(self.get_building_profiles_url(), data={'relationship': 'owner'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.owner.pk)
    
    def test_add_profile_to_building_unauthenticated_user(self):
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.regular_user.pk, 'relationship': 'tenant'})
        self.assertEqual(response.status_code, 401)
    
    def test_add_profile_to_building_request_user_is_tenant(self):
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.regular_user.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building')
    
    def test_add_profile_to_building_request_user_id_not_linked_to_building(self):
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.regular_user.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building, profile not linked to building')
    
    def test_add_profile_to_building_request_user_is_admin(self):
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.regular_user.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        building_profile = UserBuilding.objects.get(profile=self.regular_user.profile, building=self.building)
        self.assertEqual(building_profile.profile, self.regular_user.profile)
        self.assertEqual(building_profile.relationship, 'tenant')
        response = self.client.get(self.get_building_profiles_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 3)
        user_ids = list(map(lambda x: x['user']['id'], response.json()['results']))
        self.assertTrue(self.regular_user.pk in user_ids)
    
    def test_add_profile_to_building_request_user_id_owner(self):
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.regular_user.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        building_profile = UserBuilding.objects.get(profile=self.regular_user.profile, building=self.building)
        self.assertEqual(building_profile.profile, self.regular_user.profile)
        self.assertEqual(building_profile.relationship, 'tenant')
        response = self.client.get(self.get_building_profiles_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 3)
        user_ids = list(map(lambda x: x['user']['id'], response.json()['results']))
        self.assertTrue(self.regular_user.pk in user_ids)
        
    
    def test_add_profile_to_building_without_relationship_key(self):
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.regular_user.pk}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'must provide user id and relationship to building')
    
    def test_add_profile_to_building_without_user_id_key(self):
        response = self.client.patch(self.add_building_profile_url(), data={'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'must provide user id and relationship to building')

    def test_add_user_with_no_profile_to_building(self):
        self.tenant.profile.delete()
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.tenant.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'user profile does not exist')
    
    def test_add_unexisting_user_to_building(self):
        self.tenant.profile.delete()
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.tenant.pk + self.regular_user.pk + self.owner.pk + self.admin.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'user does not exist')
    
    def test_delete_building_profile_unauthenticated(self):
        response = self.client.delete(self.delete_building_profile_url())
        self.assertEqual(response.status_code, 401)

    def test_delete_building_profile_authenticated_tenant(self):
        self.regular_user.profile.buildings.add(self.building, through_defaults={'relationship': 'tenant'})
        response = self.client.delete(self.delete_building_profile_url(), headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building')

    def test_delete_building_profile_authenticated_admin(self):
        response = self.client.delete(self.delete_building_profile_url(), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(UserBuilding.DoesNotExist):
            UserBuilding.objects.get(profile=self.tenant.profile, building=self.building)

    def test_delete_building_profile_authenticated_owner(self):
        response = self.client.delete(self.delete_building_profile_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(UserBuilding.DoesNotExist):
            UserBuilding.objects.get(profile=self.tenant.profile, building=self.building)

    def test_delete_building_owner_profile(self):
        self.regular_user.profile.buildings.add(self.building, through_defaults={'relationship': 'owner'})
        response = self.client.delete(reverse('api-delete_building_profile', args=[self.building_id, self.regular_user.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(UserBuilding.DoesNotExist):
            UserBuilding.objects.get(profile=self.regular_user.profile, building=self.building)
        response = self.client.delete(reverse('api-delete_building_profile', args=[self.building_id, self.owner.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'cannot delete building only owner')
        user_building = UserBuilding.objects.get(profile=self.owner.profile, building=self.building)
        self.assertEqual(self.owner.profile, user_building.profile)
    
    def test_delete_building_unauthenticated_user(self):
        response = self.client.delete(self.get_update_building_url())
        self.assertEqual(response.status_code, 401)
    
    def test_delete_building_user_profile_not_linked_to_building(self):
        response = self.client.delete(self.get_update_building_url(), headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile is not linked to the building')
    
    def test_delete_building_user_is_tenant(self):
        response = self.client.delete(self.get_update_building_url(), headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building')
    
    def test_delete_building_user_is_owner(self):
        response = self.client.delete(self.get_update_building_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.get_update_building_url())
        self.assertEqual(response.status_code, 404)
        with self.assertRaises(Building.DoesNotExist):
            Building.objects.get(pk=self.building_id)

    def test_delete_building_user_is_admin(self):
        response = self.client.delete(self.get_update_building_url(), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.get_update_building_url())
        self.assertEqual(response.status_code, 404)
        with self.assertRaises(Building.DoesNotExist):
            Building.objects.get(pk=self.building_id)
    
    def test_delete_building_with_unresolved_notice(self):
        notice = Notice.objects.create(owner=self.owner, building=self.building, notice='rent is due')
        response = self.client.delete(self.get_update_building_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['error'], 'building has an unresolved notice')
        notice.delete()
        response = self.client.delete(self.get_update_building_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'succesfully deleted')
        response = self.client.get(self.get_update_building_url())
        self.assertEqual(response.status_code, 404)
        response = self.client.delete(self.get_update_building_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 404)
    
    def test_get_user_buildings_unauthenticated(self):
        pass

    def test_get_user_buildings_invalid_token(self):
        pass

    def test_get_user_buildings_no_query_string(self):
        pass

    def test_get_user_buildings_wrong_query_string_value(self):
        pass

    def test_get_user_buildings_authenticated(self):
        pass

    def test_get_user_buildings_authenticated_admin(self):
        pass

    def test_get_user_owned_buildings(self):
        pass

    def test_get_user_rented_buildings(self):
        pass




        