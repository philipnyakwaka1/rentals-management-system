from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
import json
from announcements.models import Notice
from buildings.models import Building

class TestBuildings(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='Yyugbcdasdd@134')
        cls.tenant = User.objects.create_user(username='tenant', password='Gyuxxcdasdd@579')
        cls.regular_user = User.objects.create_user(username='regular_user', password='Gyuxxcdasdd@579')
        cls.regular_user_token = APIClient().post(reverse('api-user_login'), {'username': 'regular_user', 'password': 'Gyuxxcdasdd@579'}).json().get('access')
        cls.owner_token = APIClient().post(reverse('api-user_login'), {'username': 'owner', 'password': 'Yyugbcdasdd@134'}).json().get('access')
        cls.tenant_token = APIClient().post(reverse('api-user_login'), {'username': 'tenant', 'password': 'Gyuxxcdasdd@579'}).json().get('access')
        cls.admin = User.objects.create_superuser(username='admin_user', password="Yyugbcdasdd@134")
        cls.admin_token = APIClient().post(reverse('api-user_login'), data={'username': 'admin_user', 'password': "Yyugbcdasdd@134"}).json()['access']
        cls.building_id = None
        cls.building_list_create_url = reverse('api-building_list_create')
        cls.building_list_by_user_url = reverse('api-buildings_list_by_user', args=[cls.owner.pk])
    
    def setUp(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-4.0, 32.5',
        }
        response = self.client.put(self.building_list_create_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.__class__.building_id = response.json().get('id')
        self.building = Building.objects.get(pk=self.building_id)
        self.tenant.profile.buildings.add(self.building, through_defaults={'relationship': 'tenant'})
    
    def building_retrieve_update_url(self):
        if self.building_id is None:
            raise ValueError('building id not yet set')
        return reverse('api-building_retrieve_update', args=[self.building_id])

    def test_get_building_unauthenticated_user(self):
        response = self.client.get(self.building_retrieve_update_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(json.loads(response.json())['features'][0]['properties']['pk']), self.building_id)
    
    def test_get_building_authenticated_user(self):
        response = self.client.get(self.building_retrieve_update_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(json.loads(response.json())['features'][0]['properties']['pk']), self.building_id)
    
    def test_create_building_unauthenticated_user(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-4.0, 32.5',
        }
        response = self.client.put(self.building_list_create_url, data)
        self.assertEqual(response.status_code, 401)

    def test_create_building_invalid_coordinates(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-4.0 32.5',
        }
        response = self.client.put(self.building_list_create_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('building')[0], 'Coordinate format cannot be parsed. The coordinate should be two floats values separated by a comma.')
        data['building'] = '-4.0, 2,4'
        response = self.client.put(self.building_list_create_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('building')[0], 'Coordinate format cannot be parsed. The coordinate should be two floats values separated by a comma.')
        data['building'] = '-4.6g, 9'
        response = self.client.put(self.building_list_create_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('building')[0], 'Coordinate format cannot be parsed. The coordinate should be two floats values separated by a comma.')
    
    def test_create_building_user_id_does_not_exist(self):
        data = {
            'user_id': self.owner.pk + self.admin.pk + self.tenant.pk + self.regular_user.pk,
            'building': '-3.0, 42.5',
        }
        response = self.client.put(self.building_list_create_url, data, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'user does not exist')

    def test_create_building_user_profile_does_not_exists(self):
        self.owner.profile.delete()
        data = {
            'user_id': self.owner.pk ,
            'building': '-3.0, 42.5',
        }
        response = self.client.put(self.building_list_create_url, data, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'user profile does not exist')

    def test_create_building_for_another_user_with_non_admin(self):
        data = {
            'user_id': self.regular_user.pk ,
            'building': '-3.0, 42.5',
        }
        response = self.client.put(self.building_list_create_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to perform this action')

    def test_create_building_for_another_user_with_admin(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-4.0, 32.5',
        }
        response = self.client.put(self.building_list_create_url, data, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 201)
        building_id = response.json().get('id')
        building = self.client.get(reverse('api-building_retrieve_update', args=[building_id]))
        self.assertEqual(building.status_code, 200)
        self.assertEqual(int(json.loads(building.json())['features'][0]['properties']['pk']), building_id)

    def test_create_building_with_authenticated_user_and_query_all_buildings(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-3.0, 42.5',
        }
        response = self.client.put(self.building_list_create_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 201)
        building_id = response.json().get('id')
        building = self.client.get(reverse('api-building_retrieve_update', args=[building_id]))
        self.assertEqual(building.status_code, 200)
        self.assertEqual(int(json.loads(building.json())['features'][0]['properties']['pk']), building_id)
        all_buildings = self.client.get(self.building_list_create_url)
        self.assertEqual(all_buildings.status_code, 200)
        self.assertEqual(len(all_buildings.json().get('results')), 2)
    
    def test_update_building_unauthenticated_user(self):
        response = self.client.patch(self.building_retrieve_update_url(), data={'building': '5.3, 42.1'})
        self.assertEqual(response.status_code, 401)
    
    def test_update_building_user_not_linked_to_building(self):
        response = self.client.patch(self.building_retrieve_update_url(), data={'building': '5.3, 42.1', 'rent': 800}, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile is not linked to the building')
    
    def test_update_building_user_not_owner(self):
        response = self.client.patch(self.building_retrieve_update_url(), data={'building': '5.3, 42.1', 'rent': 800}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building')
    
    def test_update_building_user_not_owner_but_is_admin(self):
        response = self.client.patch(self.building_retrieve_update_url(), data={'building': '5.3, 42.1', 'rent': 800}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        building = json.loads(self.client.get(self.building_retrieve_update_url()).json())
        self.assertEqual(building['features'][0]['geometry']['coordinates'][0], 42.1)
        self.assertEqual(building['features'][0]['geometry']['coordinates'][1], 5.3)
    
    def test_update_building_authenticated_owner(self):
        response = self.client.patch(self.building_retrieve_update_url(), data={'building': '5.3, 42.1'},headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        building = json.loads(self.client.get(self.building_retrieve_update_url(), data={'geojson': 'true'}).json())
        self.assertEqual(building['features'][0]['geometry']['coordinates'][0], 42.1)
        self.assertEqual(building['features'][0]['geometry']['coordinates'][1], 5.3)
    
    def test_delete_building_unauthenticated_user(self):
        response = self.client.delete(self.building_retrieve_update_url())
        self.assertEqual(response.status_code, 401)
    
    def test_delete_building_user_profile_not_linked_to_building(self):
        response = self.client.delete(self.building_retrieve_update_url(), headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile is not linked to the building')
    
    def test_delete_building_user_is_tenant(self):
        response = self.client.delete(self.building_retrieve_update_url(), headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building')
    
    def test_delete_building_user_is_owner(self):
        response = self.client.delete(self.building_retrieve_update_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.building_retrieve_update_url())
        self.assertEqual(response.status_code, 404)
        with self.assertRaises(Building.DoesNotExist):
            Building.objects.get(pk=self.building_id)

    def test_delete_building_user_is_admin(self):
        response = self.client.delete(self.building_retrieve_update_url(), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.building_retrieve_update_url())
        self.assertEqual(response.status_code, 404)
        with self.assertRaises(Building.DoesNotExist):
            Building.objects.get(pk=self.building_id)

    def test_delete_building_with_unresolved_notice(self):
        notice = Notice.objects.create(owner=self.owner, building=self.building, notice='rent is due')
        response = self.client.delete(self.building_retrieve_update_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['error'], 'building has an unresolved notice')
        notice.delete()
        response = self.client.delete(self.building_retrieve_update_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'succesfully deleted')
        response = self.client.get(self.building_retrieve_update_url())
        self.assertEqual(response.status_code, 404)
        response = self.client.delete(self.building_retrieve_update_url(), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 404)

    def test_get_user_buildings_unauthenticated(self):
        response = self.client.get(self.building_list_by_user_url, data={'category': 'owner'})
        self.assertEqual(response.status_code, 401)

    def test_get_user_buildings_invalid_token(self):
        response = self.client.get(self.building_list_by_user_url, data={'category': 'owner'}, headers={'Authorization': f'Bearer Invalid_Token'})
        self.assertEqual(response.status_code, 401)

    def test_get_user_buildings_no_query_string(self):
        response = self.client.get(self.building_list_by_user_url, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Missing or invalid 'category' query parameter. Expected 'owner' or 'tenant'.")

    def test_get_user_buildings_wrong_query_string_value(self):
        response = self.client.get(self.building_list_by_user_url, data={'category': 'owned'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Missing or invalid 'category' query parameter. Expected 'owner' or 'tenant'.")

    def test_get_user_buildings_authenticated_owner(self):
        response = self.client.get(self.building_list_by_user_url, data={'category': 'owner'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['id'], self.building_id)
        response = self.client.get(self.building_list_by_user_url, data={'category': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.json()['results'], [])
    
    def test_get_user_buildings_authenticated_tenant(self):
        response = self.client.get(reverse('api-buildings_list_by_user', args=[self.tenant.pk]), data={'category': 'tenant'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['id'], self.building_id)
        response = self.client.get(reverse('api-buildings_list_by_user', args=[self.tenant.pk]), data={'category': 'owner'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.json()['results'], [])

    def test_get_another_user_buildings_authenticated_admin(self):
        response = self.client.get(self.building_list_by_user_url, data={'category': 'owner'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['id'], self.building_id)
        response = self.client.get(self.building_list_by_user_url, data={'category': 'tenant'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.json()['results'], [])
        response = self.client.get(reverse('api-buildings_list_by_user', args=[self.admin.pk]), data={'category': 'owner'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.json()['results'], [])

    def test_get_another_user_buildings(self):
        response = self.client.get(self.building_list_by_user_url, data={'category': 'owner'}, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to perform this action')
    
    def test_get_unexisting_user_buildings(self):
        response = self.client.get(reverse('api-buildings_list_by_user', args=[self.admin.pk + self.tenant.pk + self.owner.pk + self.regular_user.pk]), data={'category': 'owned'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'user does not exist')
    
    def test_get_unexisting_profile_user_buildings(self):
        self.regular_user.profile.delete()
        response = self.client.get(reverse('api-buildings_list_by_user', args=[self.regular_user.pk]), data={'category': 'owned'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'user profile does not exist')



        