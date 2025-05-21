from rest_framework.test import APIClient, APITestCase
from buildings.api.v1 import views
from django.contrib.auth.models import User
from django.urls import reverse
import json
from announcements.models import Notice, Comment
from buildings.models import Building

class TestBuildings(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='user1', password='user1@123')
        cls.user2 = User.objects.create_user(username='user2', password='user2@123')
        cls.access_token = APIClient().post(reverse('JWT-login_view'), {'username': 'user1', 'password': 'user1@123'}).json().get('access')
        cls.id = None
        cls.create_query_url = reverse('api-create_query_building')
    
    def setUp(self):
        data = {
            'user_id': self.user1.pk,
            'building': '-4.0, 32.5',
        }
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.access_token}'})
        self.__class__.id = response.json().get('id')
    
    def get_update_url(self):
        if self.__class__.id is None:
            raise ValueError('building id not yet set')
        return reverse('api-get_update_building', args=[self.__class__.id])
    
    def get_building_profiles(self):
        if self.__class__.id is None:
            raise ValueError('building id not set')
        return reverse('api-building_users', args=[self.__class__.id])
    
    def add_building_profile(self):
        if self.__class__.id is None:
            raise ValueError('building id not set')
        return reverse('api-add_building_profile', args=[self.__class__.id])

    def test_create_query_building_authenticated(self):
        data = {
            'user_id': self.user1.pk,
            'building': '-3.0, 42.5',
        }
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        self.__class__.id = response.json().get('id')
        building = self.client.get(self.get_update_url(), headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(building.status_code, 200)
        self.assertEqual(int(json.loads(building.json())['features'][0]['properties']['pk']), self.__class__.id)
        all_buildings = self.client.get(self.create_query_url)
        self.assertEqual(all_buildings.status_code, 200)
        self.assertEqual(len(all_buildings.json().get('results')), 2)


    def test_create_query_building_unauthenticated(self):
        data = {
            'user_id': self.user1.pk,
            'building': '-4.0, 32.5',
        }
        response_401 = self.client.put(self.create_query_url, data)
        self.assertEqual(response_401.status_code, 401)
        response_200 = self.client.get(self.get_update_url())
        self.assertEqual(response_200.status_code, 200)
        self.assertEqual(int(json.loads(response_200.json())['features'][0]['properties']['pk']), self.__class__.id)

    def test_create_building_invalid_coordinates(self):
        data = {
            'user_id': self.user1.pk,
            'building': '-4.0 32.5',
        }
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('building')[0], 'Coordinate format cannot be parsed. The coordinate should be two floats values separated by a comma.')
        data['building'] = '-4.0, 2,4'
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('building')[0], 'Coordinate format cannot be parsed. The coordinate should be two floats values separated by a comma.')
        data['building'] = '-4.6g, 9'
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('building')[0], 'Coordinate format cannot be parsed. The coordinate should be two floats values separated by a comma.')
    
    def test_update_building(self):
        response_unauth = self.client.patch(self.get_update_url(), data={'building': '5.3, 42.1'})
        self.assertEqual(response_unauth.status_code, 401)
        response_auth = self.client.patch(self.get_update_url(), data={'building': '5.3, 42.1'},headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response_auth.status_code, 200)
        building = json.loads(self.client.get(self.get_update_url(), data={'geojson': 'true'}).json())
        self.assertEqual(building['features'][0]['geometry']['coordinates'][0], 42.1)
        self.assertEqual(building['features'][0]['geometry']['coordinates'][1], 5.3)
    
    def test_get_building_profiles(self):
        response = self.client.get(self.get_building_profiles())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.user1.pk)
    
    def test_add_profile_to_building(self):
        response = self.client.patch(self.add_building_profile(), data={'user_id': self.user2.pk, 'relationship': 'tenant'})
        self.assertEqual(response.status_code, 401)
        response = self.client.patch(self.add_building_profile(), data={'user_id': self.user2.pk}, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'must provide user id and relationship to building')
        response = self.client.patch(self.add_building_profile(), data={'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'must provide user id and relationship to building')
        response = self.client.patch(self.add_building_profile(), data={'user_id': self.user2.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], f'profile with user id {self.user2.pk} successful added to building id {self.__class__.id}')
        response = self.client.get(self.get_building_profiles())
        linked_users = list(map(lambda x: x['user']['id'], response.json()['results']))
        self.assertEqual(len(linked_users), 2)
        self.assertTrue(self.user1.pk in linked_users)
        self.assertTrue(self.user2.pk in linked_users)
        
    def test_comments(self):
        building = Building.objects.get(pk=self.__class__.id)
        comment1 = Comment.objects.create(tenant=self.user2, building=building, comment='leaking roof')
        comment2 = Comment.objects.create(tenant=self.user2, building=building, comment='door knob is broken')
        response = self.client.get(reverse('api-building_comments', args=[self.__class__.id]))
        self.assertEqual(response.status_code, 200)
        print(response.json())
        self.assertEqual(len(response.json()['results']), 2)
    
    def test_notices(self):
        building = Building.objects.get(pk=self.__class__.id)
        notice1 = Notice.objects.create(owner=self.user1, building=building, notice='rent is due')
        notice2 = Notice.objects.create(owner=self.user1, building=building, notice='party for tenants')
        response = self.client.get(reverse('api-building_notices', args=[self.__class__.id]))
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 2)
        