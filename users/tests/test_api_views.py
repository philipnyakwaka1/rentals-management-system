from rest_framework.test import APITestCase, APIClient
from users.api.v1 import views
from django.urls import reverse
from django.contrib.auth.models import User
from announcements.models import Notice
from buildings.models import Building
from buildings.api.v1 import views as building_views
import math



class TestUserRegistration(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api-register_users')

    def test_succesful_create_account(self):
        response = self.client.put(self.url, {'username': 'test_user', 'password': 'Yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 201)
        self.assertTrue('id' in response.json().keys())
        self.assertTrue('username' in response.json().keys())

    def test_existing_username(self):
        user1_response = self.client.put(self.url, {'username': 'test_user', 'password': 'Yyugbcdasdd@134'})
        user2_response = self.client.put(self.url, {'username': 'test_user', 'password': 'Wyuxvbtdghsd@765'})
        self.assertEqual(user2_response.status_code, 400)
        self.assertEqual(user2_response.json()['error'], 'username already exists')

    def test_no_password(self):
        response = self.client.put(self.url, {'username': 'test_user'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': ['This field is required.']})

    def test_no_username(self):
        response = self.client.put(self.url, {'password': 'Yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'username': ['This field is required.']})

    def test_short_password(self):
        response = self.client.put(self.url, {'username': 'test_user', 'password': 'Yd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': {'error': ['password must be at least 8 characters long']}})

    def test_password_no_uppercase(self):
        response = self.client.put(self.url, {'username': 'test_user', 'password': 'yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': {'error': ['password must contain at least 1 uppercase character']}})

    def test_password_no_special(self):
        response = self.client.put(self.url, {'username': 'test_user', 'password': 'Yyugbcdasdd134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': {'error': ['password must contain at least 1 special character']}})

    def test_password_no_number(self):
        response = self.client.put(self.url, {'username': 'test_user', 'password': 'Yyugbcdasdd@'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': {'error': ['password must contain at least 1 number']}})

    def test_password_all_criteria_fail(self):
        response = self.client.put(self.url, {'username': 'test_user', 'password': 'yy'})
        self.assertEqual(response.status_code, 400)
        self.assertTrue('password must be at least 8 characters long' in response.json()['password']['error'])
        self.assertTrue('password must contain at least 1 uppercase character' in response.json()['password']['error'])
        self.assertTrue('password must contain at least 1 special character' in response.json()['password']['error'])
        self.assertTrue('password must contain at least 1 number' in response.json()['password']['error'])


class TestUserLoginCredentials(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.register_url = reverse('api-register_users')
        cls.login_url = reverse('JWT-login_view')
        cls.user_register_response = APIClient().put(cls.register_url, {'username': 'test_user', 'password': 'Yyugbcdasdd@134'})
    
    def test_correct_login_credentials(self):
        response = self.client.post(self.login_url, {'username': 'test_user', 'password': 'Yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('access'))
        self.assertTrue(response.cookies.get('refresh_token'))
        self.assertTrue(self.client.cookies.get('refresh_token'))
    
    def test_incorrect_username(self):
        response = self.client.post(self.login_url, {'username': 'Test_user', 'password': 'Yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'invalid login credentials')
    
    def test_incorrect_password(self):
        response = self.client.post(self.login_url, {'username': 'test_user', 'password': 'yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'invalid login credentials')

class TestAllUserDataAPI(APITestCase):

    @classmethod
    def setUpTestData(cls):
        for i in range(15):
            User.objects.create_user(username=f'test_user{i}', password=f'Tyugbcdasdd@134{i}')
        cls.admin = User.objects.create_superuser('admin_user', 'admin_user@gmail.com', 'Yyugbcdasdd@134')
        cls.normal_user = APIClient().put(reverse('api-register_users'), {'username': 'test_user', 'password': 'RDngdgssv@345'})
        cls.admin_token = APIClient().post(reverse('JWT-login_view'), {'username': 'admin_user', 'password': 'Yyugbcdasdd@134'}).json().get('access')
        cls.normal_token = APIClient().post(reverse('JWT-login_view'), {'username': 'test_user', 'password': 'RDngdgssv@345'}).json().get('access')
        cls.all_users_url = reverse('api-get_users')
    
    def test_get_users_api_admin_access(self):
        normal_client_response = APIClient().get(self.all_users_url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(normal_client_response.status_code, 403)
        admin_client_response = APIClient().get(self.all_users_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(admin_client_response.status_code, 200)
    
    def test_get_users_api_paginated_response(self):
        response = self.client.get(self.all_users_url, headers={'Authorization': f'Bearer {self.admin_token}'}).json()
        users = User.objects.all()
        self.assertEqual(len(response['results']), 5)
        self.assertFalse(response['previous'])
        self.assertTrue(response['next'])
        total_pages = math.ceil(len(users) / 5)
        last_page = self.client.get(self.all_users_url + f'?page={total_pages}', headers={'Authorization': f'Bearer {self.admin_token}'}).json()
        self.assertTrue(last_page['previous'])
        self.assertFalse(last_page['next'])
        first_10_items = self.client.get(self.all_users_url + '?page=1&page_size=10', headers={'Authorization': f'Bearer {self.admin_token}'}).json()['results']
        self.assertEqual(len(first_10_items), 10)
        invalid_page = self.client.get(self.all_users_url + f'?page={total_pages + 1}', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(invalid_page.status_code, 404)


class TestSpecificUserEndpoint(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('admin_user', 'admin_user@gmail.com', 'Yyugbcdasdd@134')
        cls.normal_user = APIClient().put(reverse('api-register_users'), {'username': 'test_user', 'password': 'RDngdgssv@345'})
        cls.admin_token = APIClient().post(reverse('JWT-login_view'), {'username': 'admin_user', 'password': 'Yyugbcdasdd@134'}).json().get('access')
        cls.normal_token = APIClient().post(reverse('JWT-login_view'), {'username': 'test_user', 'password': 'RDngdgssv@345'}).json().get('access')
        cls.user_id = cls.normal_user.json()['id']

    def test_get_user(self):
        invalid_token_acess = self.client.get(reverse('api-update_user', args=[self.user_id]), headers={'Authorization': f'Bearer invalid-token'})
        self.assertEqual(invalid_token_acess.status_code, 401)
        unauthorized_access = self.client.get(reverse('api-update_user', args=[self.user_id]))
        self.assertEqual(unauthorized_access.status_code, 401)
        response = self.client.get(reverse('api-update_user', args=[self.user_id]), headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.user_id)
        self.assertEqual(response.json()['username'], 'test_user')

    
    def test_get_users_api_no_users(self):
        response = self.client.get(reverse('api-update_user', args=[self.user_id + 1]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
    
    def test_get_another_user_data(self):
        user_2_id = self.client.put(reverse('api-register_users'), {'username': 'test_user2', 'password': 'RDngdgssv@345'}).json().get('id')
        normal_user_response = self.client.get(reverse('api-update_user', args=[user_2_id]), headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(normal_user_response.status_code, 403)
        admin_response = self.client.get(reverse('api-update_user', args=[user_2_id]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(admin_response.status_code, 200)
    
    def test_update_user(self):
        response = self.client.patch(reverse('api-update_user', args=[self.__class__.user_id]), data={'first_name': 'updated_fn'},headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('api-update_user', args=[self.__class__.user_id]), headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.json()['first_name'], 'updated_fn')

    def test_delete_user(self):
        user = User.objects.get(pk=self.__class__.user_id)
        building = self.client.put(reverse('api-create_query_building'), data={'user_id': user.pk, 'building': '-4.5, 33.7'},  headers={'Authorization': f'Bearer {self.normal_token}'})
        building = Building.objects.get(pk=building.json()['id'])
        notice = Notice.objects.create(owner=user, building=building, notice='rent is due')
        response = self.client.delete(reverse('api-update_user', args=[self.__class__.user_id]), headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 409)
        notice.delete()
        response = self.client.delete(reverse('api-update_user', args=[self.__class__.user_id]), headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.delete(reverse('api-update_user', args=[self.__class__.user_id]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse('api-update_user', args=[self.__class__.user_id]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)


class TestUserProfile(APITestCase):
    
    @classmethod
    def setUpTestData(cls):
        register_user = APIClient().put(reverse('api-register_users'), data={'username': 'test_user', 'password': 'RDngdgssv@345'})
        login_user = APIClient().post(reverse('JWT-login_view'), data={'username': 'test_user', 'password': 'RDngdgssv@345'})
        cls.access_token = login_user.json().get('access')
        cls.user_id = register_user.json().get('id')
        cls.profile_url = reverse('api-get_update_profile', args=[cls.user_id])
        cls.profile_buildings_url = reverse('api-user_buildings', args=[cls.user_id])
        cls.buildings_url = reverse('api-create_query_building')
    
    def test_get_another_user_profile(self):
        response = self.client.get(reverse('api-get_update_profile', args=[self.__class__.user_id + 1]), headers={'Authorization': f'Bearer {self.__class__.access_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_get_user_profile(self):
        response = self.client.get(self.__class__.profile_url)
        self.assertEqual(response.status_code, 401)
        response = self.client.get(self.__class__.profile_url, headers={'Authorization': f'Bearer {self.__class__.access_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['id'], self.__class__.user_id)
        self.assertTrue(response.json()['user']['profile'] is not None)

    def test_update_user_profile(self):
        response = self.client.patch(self.__class__.profile_url, data={'phone': '05XX', 'address': 'Jean Deux Park'}, headers={'Authorization': f'Bearer {self.__class__.access_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.__class__.profile_url, headers={'Authorization': f'Bearer {self.__class__.access_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['profile']['phone'], '05XX')
        self.assertEqual(response.json()['user']['profile']['address'], 'Jean Deux Park')
    
    def test_delete_user_profile(self):
        response = self.client.delete(self.__class__.profile_url, headers={'Authorization': f'Bearer {self.__class__.access_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.__class__.profile_url, headers={'Authorization': f'Bearer {self.__class__.access_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'profile does not exist')
    
    def test_user_buildings(self):
         response = self.client.get(self.__class__.profile_buildings_url, headers={'Authorization': f'Bearer {self.__class__.access_token}'})
         self.assertEqual(response.status_code, 200)
         self.assertEqual(len(response.json()['results']), 0)
         building1 = self.client.put(self.__class__.buildings_url, data={'user_id': self.__class__.user_id, 'building': '-4.5, 33.7'},  headers={'Authorization': f'Bearer {self.__class__.access_token}'})
         building2 = self.client.put(self.__class__.buildings_url, data={'user_id': self.__class__.user_id, 'building': '-2.6, 34.1'},  headers={'Authorization': f'Bearer {self.__class__.access_token}'})
         response = self.client.get(self.__class__.profile_buildings_url, headers={'Authorization': f'Bearer {self.__class__.access_token}'})
         self.assertEqual(response.status_code, 200)
         self.assertEqual(len(response.json()['results']), 2)
    
