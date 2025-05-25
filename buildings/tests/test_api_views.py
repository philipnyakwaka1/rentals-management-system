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
        cls.owner = User.objects.create_user(username='owner', password='Yyugbcdasdd@134')
        cls.normal_user = User.objects.create_user(username='normal_user', password='Gyuxxcdasdd@579')
        cls.owner_token = APIClient().post(reverse('JWT-login_view'), {'username': 'owner', 'password': 'Yyugbcdasdd@134'}).json().get('access')
        cls.normal_user_token = APIClient().post(reverse('JWT-login_view'), {'username': 'normal_user', 'password': 'Gyuxxcdasdd@579'}).json().get('access')
        cls.building_id = None
        cls.create_query_url = reverse('api-create_query_building')
    
    def setUp(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-4.0, 32.5',
        }
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.__class__.building_id = response.json().get('id')
    
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
    
    def get_building_comments_url(self):
        if self.building_id is None:
            raise ValueError('building id not set')
        return reverse('api-building_comments', args=[self.building_id])
    
    def get_building_notices_url(self):
        if self.building_id is None:
            raise ValueError('building id not set')
        return reverse('api-building_notices', args=[self.building_id])
    
    def test_get_building(self):
        response_unauthenticated = self.client.get(self.get_update_building_url())
        self.assertEqual(response_unauthenticated.status_code, 200)
        self.assertEqual(int(json.loads(response_unauthenticated.json())['features'][0]['properties']['pk']), self.building_id)
        response_authenticated = self.client.get(self.get_update_building_url())
        self.assertEqual(response_authenticated.status_code, 200)
        self.assertEqual(int(json.loads(response_authenticated.json())['features'][0]['properties']['pk']), self.building_id)
    
    def test_create_building_unauthenticated_user(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-4.0, 32.5',
        }
        response = self.client.put(self.create_query_url, data)
        self.assertEqual(response.status_code, 401)

    def test_create_building_with_authenticated_user_and_query_all_buildings(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-3.0, 42.5',
        }
        response = self.client.put(self.create_query_url, data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 201)
        building_id = response.json().get('id')
        building = self.client.get(self.get_update_building_url())
        self.assertEqual(building.status_code, 200)
        self.assertEqual(int(json.loads(building.json())['features'][0]['properties']['pk']), self.building_id)
        all_buildings = self.client.get(self.create_query_url)
        self.assertEqual(all_buildings.status_code, 200)
        self.assertEqual(len(all_buildings.json().get('results')), 2)
    
    
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

    
    def test_update_building_unauthenticated_user(self):
        response = self.client.patch(self.get_update_building_url(), data={'building': '5.3, 42.1'})
        self.assertEqual(response.status_code, 401)
    
    def test_update_building_authenticated_user(self):
        response = self.client.patch(self.get_update_building_url(), data={'building': '5.3, 42.1'},headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        building = json.loads(self.client.get(self.get_update_building_url(), data={'geojson': 'true'}).json())
        self.assertEqual(building['features'][0]['geometry']['coordinates'][0], 42.1)
        self.assertEqual(building['features'][0]['geometry']['coordinates'][1], 5.3)
    
    def test_update_building_user_not_linked_to_building(self):
        response = self.client.patch(self.get_update_building_url(), data={'building': '5.3, 42.1', 'rent': '$800'}, headers={'Authorization': f'Bearer {self.normal_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile is not linked to the building')
    
    def test_update_building_user_not_owner(self):
        self.normal_user.profile.buildings.add(Building.objects.get(pk=self.building_id), through_defaults={'relationship': 'tenant'})
        response = self.client.patch(self.get_update_building_url(), data={'building': '5.3, 42.1', 'rent': '$800'}, headers={'Authorization': f'Bearer {self.normal_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building')


    def test_get_building_profiles(self):
        response = self.client.get(self.get_building_profiles_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.owner.pk)
    
    def test_add_profile_to_building_unauthenticated_user(self):
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.normal_user.pk, 'relationship': 'tenant'})
        self.assertEqual(response.status_code, 401)
    
    def test_add_profile_to_building_without_relationship_key(self):
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.normal_user.pk}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'must provide user id and relationship to building')
    
    def test_add_profile_to_building_without_user_id_key(self):
        response = self.client.patch(self.add_building_profile_url(), data={'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'must provide user id and relationship to building')

    def test_add_user_with_no_profile_to_building(self):
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.normal_user.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.normal_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building, profile not linked to building')

    def test_add_profile_to_another_users_buildings(self):
        self.normal_user.profile.buildings.add(Building.objects.get(pk=self.building_id), through_defaults={'relationship': 'tenant'})
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.normal_user.pk, 'relationship': 'owner'}, headers={'Authorization': f'Bearer {self.normal_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building')
    
    def test_add_profile_to_building_authenticated_user_and_get_building_profiles_url(self):
        response = self.client.patch(self.add_building_profile_url(), data={'user_id': self.normal_user.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], f'profile with user id {self.normal_user.pk} successful added to building id {self.building_id}')
        response = self.client.get(self.get_building_profiles_url())
        self.assertEqual(response.status_code, 200)
        linked_users = list(map(lambda x: x['user']['id'], response.json()['results']))
        self.assertEqual(len(linked_users), 2)
        self.assertTrue(self.owner.pk in linked_users)
        self.assertTrue(self.normal_user.pk in linked_users)
    
    def test_comment_unexisting_building(self):
        response = self.client.get(reverse('api-building_comments', args=[self.building_id + 1]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'Building does not exist')
        
    def test_all_building_comments(self):
        building = Building.objects.get(pk=self.building_id)
        comment1 = Comment.objects.create(tenant=self.normal_user, building=building, comment='leaking roof')
        comment2 = Comment.objects.create(tenant=self.normal_user, building=building, comment='door knob is broken')
        response = self.client.get(self.get_building_comments_url())
        self.assertEqual(response.status_code, 200)
        all_comments = list(map(lambda x: x['pk'], response.json()['results']))
        self.assertEqual(len(all_comments), 2)
        self.assertTrue(comment1.pk in all_comments and comment2.pk in all_comments)
    
    def test_notice_unexisting_building(self):
        response = self.client.get(reverse('api-building_notices', args=[self.building_id + 1]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'Building does not exist')
        
    def test_all_building_notices(self):
        building = Building.objects.get(pk=self.building_id)
        notice1 = Notice.objects.create(owner=self.owner, building=building, notice='rent is due')
        notice2 = Notice.objects.create(owner=self.owner, building=building, notice='you exhausted your deposit')
        response = self.client.get(self.get_building_notices_url())
        self.assertEqual(response.status_code, 200)
        all_notices = list(map(lambda x: x['pk'], response.json()['results']))
        self.assertEqual(len(all_notices), 2)
        self.assertTrue(notice1.pk in all_notices and notice2.pk in all_notices)
    
    def test_delete_building_unauthenticated_user(self):
        response = self.client.delete(self.get_update_building_url())
        self.assertEqual(response.status_code, 401)
    
    def test_delete_building_user_profile_not_linked_to_building(self):
        response = self.client.delete(self.get_update_building_url(), headers={'Authorization': f'Bearer {self.normal_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile is not linked to the building')
    
    def test_delete_building_user_not_owner(self):
        self.normal_user.profile.buildings.add(Building.objects.get(pk=self.building_id), through_defaults={'relationship': 'tenant'})
        response = self.client.delete(self.get_update_building_url(), headers={'Authorization': f'Bearer {self.normal_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building')
    
    def test_delete_building_with_unresolved_notice(self):
        building = Building.objects.get(pk=self.building_id)
        notice = Notice.objects.create(owner=self.owner, building=building, notice='rent is due')
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




        