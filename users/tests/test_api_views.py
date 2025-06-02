from rest_framework.test import APITestCase, APIClient
from users.api.v1 import views
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Profile
from announcements.models import Notice
from buildings.models import Building
from buildings.api.v1 import views as building_views
import math
from datetime import datetime



class TestUserRegistration(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api-register_users')

    def test_succesful_create_account(self):
        response = self.client.put(self.url, data={'username': 'test_user', 'password': 'Yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(pk=response.json()['id'])
        self.assertEqual(response.json()['username'], user.username)
        

    def test_create_user_existing_username(self):
        self.client.put(self.url, data={'username': 'test_user', 'password': 'Yyugbcdasdd@134'})
        response = self.client.put(self.url, {'username': 'test_user', 'password': 'Wyuxvbtdghsd@765'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'username already exists')
        existing_user = User.objects.filter(username='test_user')
        self.assertEqual(len(existing_user), 1)

    def test_create_user_no_password(self):
        response = self.client.put(self.url, data={'username': 'test_user'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': ['This field is required.']})

    def test_create_user_no_username(self):
        response = self.client.put(self.url, data={'password': 'Yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'username': ['This field is required.']})

    def test_create_user_short_password(self):
        response = self.client.put(self.url, data={'username': 'test_user', 'password': 'Yd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': {'error': ['password must be at least 8 characters long']}})

    def test_create_user_password_no_uppercase(self):
        response = self.client.put(self.url, {'username': 'test_user', 'password': 'yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': {'error': ['password must contain at least 1 uppercase character']}})

    def test_create_user_password_no_special(self):
        response = self.client.put(self.url, {'username': 'test_user', 'password': 'Yyugbcdasdd134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': {'error': ['password must contain at least 1 special character']}})

    def test_create_user_password_no_number(self):
        response = self.client.put(self.url, {'username': 'test_user', 'password': 'Yyugbcdasdd@'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': {'error': ['password must contain at least 1 number']}})

    def test_create_user_all_password_criteria_fail(self):
        response = self.client.put(self.url, {'username': 'test_user', 'password': 'yy'})
        self.assertEqual(response.status_code, 400)
        self.assertTrue('password must be at least 8 characters long' in response.json()['password']['error'])
        self.assertTrue('password must contain at least 1 uppercase character' in response.json()['password']['error'])
        self.assertTrue('password must contain at least 1 special character' in response.json()['password']['error'])
        self.assertTrue('password must contain at least 1 number' in response.json()['password']['error'])



class TestUserLogin(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.register_url = reverse('api-register_users')
        cls.login_url = reverse('JWT-login_view')
        cls.user = APIClient().put(cls.register_url, data={'username': 'test_user', 'password': 'Yyugbcdasdd@134'})
    
    def test_login_correct_credentials(self):
        response = self.client.post(self.login_url, data={'username': 'test_user', 'password': 'Yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('access'))
        self.assertTrue(response.cookies.get('refresh_token'))
        self.assertTrue(self.client.cookies.get('refresh_token'))
    
    def test_login_incorrect_username(self):
        response = self.client.post(self.login_url, data={'username': 'Test_user', 'password': 'Yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'invalid login credentials')
    
    def test_login_incorrect_password(self):
        response = self.client.post(self.login_url, {'username': 'test_user', 'password': 'yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'invalid login credentials')
    
    def test_login_incorrect_username_and_password(self):
        response = self.client.post(self.login_url, {'username': 'Test_user', 'password': 'YyuGc90dasdd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'invalid login credentials')


class TestAllUsers(APITestCase):

    @classmethod
    def setUpTestData(cls):
        for i in range(15):
            User.objects.create_user(username=f'test_user{i}', password=f'Tyugbcdasdd@134{i}')
        cls.admin = User.objects.create_superuser(username='admin_user', email='admin_user@gmail.com', password='Yyugbcdasdd@134')
        cls.normal_user = APIClient().put(reverse('api-register_users'), data={'username': 'test_user', 'password': 'RDngdgssv@345'})
        cls.admin_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'admin_user', 'password': 'Yyugbcdasdd@134'}).json().get('access')
        cls.normal_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'test_user', 'password': 'RDngdgssv@345'}).json().get('access')
        cls.all_users_url = reverse('api-get_users')
    
    def test_get_all_users_unauthenticated(self):
        response = APIClient().get(self.all_users_url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)

    def test_get_all_users_authenticated_not_admin(self):
        response = APIClient().get(self.all_users_url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)

    def test_get_users_api_admin(self):
        response = APIClient().get(self.all_users_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        users = User.objects.all()
        self.assertEqual(len(response.json()['results']), 5)
        self.assertFalse(response.json()['previous'])
        self.assertTrue(response.json()['next'])
        total_pages = math.ceil(len(users) / 5)
        last_page = self.client.get(self.all_users_url + f'?page={total_pages}', headers={'Authorization': f'Bearer {self.admin_token}'}).json()
        self.assertTrue(last_page['previous'])
        self.assertFalse(last_page['next'])
        first_10_items = self.client.get(self.all_users_url + '?page=1&page_size=10', headers={'Authorization': f'Bearer {self.admin_token}'}).json()['results']
        self.assertEqual(len(first_10_items), 10)
        invalid_page = self.client.get(self.all_users_url + f'?page={total_pages + 1}', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(invalid_page.status_code, 404)


class TestUser(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('admin_user', 'admin_user@gmail.com', 'Yyugbcdasdd@134')
        cls.admin_token = APIClient().post(reverse('JWT-login_view'), {'username': 'admin_user', 'password': 'Yyugbcdasdd@134'}).json().get('access')
    
    def setUp(self):
        self.normal_user = User.objects.create_user(username='test_user', password='RDngdgssv@345')
        self.normal_token = APIClient().post(reverse('JWT-login_view'), {'username': 'test_user', 'password': 'RDngdgssv@345'}).json().get('access')
        self.url = reverse('api-update_user', args=[self.normal_user.pk])

    def test_get_user_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
    
    def test_get_user_inavalid_token(self):
        response = self.client.get(self.url, headers={'Authorization': f'Bearer invalid-token'})
        self.assertEqual(response.status_code, 401)

    def test_get_user_authenticated(self):
        response = self.client.get(self.url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.normal_user.pk)
        self.assertEqual(response.json()['username'], 'test_user')
    
    def test_get_user_another_user_account_normal_user(self):
        response = self.client.get(reverse('api-update_user', args=[self.admin.pk]), headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user not authorized to perform this action')

    def test_get_user_another_user_account_admin(self):
        response = self.client.get(self.url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.normal_user.pk)
        self.assertEqual(response.json()['username'], 'test_user')

    def test_get_unexisting_user(self):
        response = self.client.get(reverse('api-update_user', args=[self.normal_user.pk + self.admin.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)

    def test_update_user_unauthenticated(self):
        response = self.client.patch(self.url, data={'first_name': 'updated_fn'})
        self.assertEqual(response.status_code, 401)
    
    def test_update_user_inavalid_token(self):
        response = self.client.patch(self.url, data={'first_name': 'updated_fn'}, headers={'Authorization': f'Bearer invalid-token'})
        self.assertEqual(response.status_code, 401)

    def test_update_user_authenticated(self):
        response = self.client.patch(self.url, data={'first_name': 'updated_fn'}, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(pk=self.normal_user.pk)
        self.assertEqual(user.first_name, 'updated_fn')
    
    def test_update_user_another_user_account_normal_user(self):
        response = self.client.patch(reverse('api-update_user', args=[self.admin.pk]), data={'first_name': 'updated_fn'}, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)

    def test_update_user_another_user_account_admin(self):
        response = self.client.patch(self.url, data={'first_name': 'updated_fn'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(pk=self.normal_user.pk)
        self.assertEqual(user.first_name, 'updated_fn')

    def test_update_unexisting_user(self):
        response = self.client.patch(reverse('api-update_user', args=[self.admin.pk + self.normal_user.pk]), data={'first_name': 'updated_fn'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)

    def test_update_read_only_user_fields(self):
        date_joined = self.normal_user.date_joined
        last_login = self.normal_user.last_login
        updated_date_joined = datetime.now()
        updated_last_login = datetime.now()
        response = self.client.patch(self.url, data={'first_name': 'updated_fn', 'last_login': updated_last_login, 'date_joined': updated_date_joined}, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(pk=self.normal_user.pk)
        self.assertEqual(user.first_name, 'updated_fn')
        self.assertEqual(date_joined, user.date_joined)
        self.assertEqual(last_login, user.last_login)

    def test_delete_user_unauthenticated(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)
    
    def test_delete_user_inavalid_token(self):
        response = self.client.delete(self.url,headers={'Authorization': f'Bearer invalid_token'})
        self.assertEqual(response.status_code, 401)

    def test_delete_user_authenticated(self):
        response = self.client.delete(self.url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.normal_user.pk)

    def test_delete_user_unresolved_notice(self):
        response = self.client.put(reverse('api-create_query_building'), data={'user_id': self.normal_user.pk, 'building': '-4.5, 33.7'},  headers={'Authorization': f'Bearer {self.normal_token}'})
        building = Building.objects.get(pk=response.json()['id'])
        notice = Notice.objects.create(owner=self.normal_user, building=building, notice='rent is due')
        response = self.client.delete(self.url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 409)
        notice.delete()
        response = self.client.delete(self.url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.delete(self.url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        response = self.client.get(self.url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)

    
    def test_delete_user_another_user_account_normal_user(self):
        response = self.client.delete(reverse('api-update_user', args=[self.admin.pk]), headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)

    def test_delete_user_another_user_account_admin(self):
        response = self.client.delete(self.url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.normal_user.pk)

    def test_delete_unexisting_user(self):
        response = self.client.delete(reverse('api-update_user', args=[self.admin.pk + self.normal_user.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)        

class TestUserProfile(APITestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('admin_user', 'admin_user@gmail.com', 'Yyugbcdasdd@134')
        cls.admin_token = APIClient().post(reverse('JWT-login_view'), {'username': 'admin_user', 'password': 'Yyugbcdasdd@134'}).json().get('access')

    def setUp(self):
        self.normal_user = User.objects.create_user(username='test_user', password='RDngdgssv@345')
        self.normal_user.profile.phone = '0XXXX'
        self.normal_user.profile.address = 'Jumuiya Road'
        self.normal_user.profile.save()
        self.normal_token = APIClient().post(reverse('JWT-login_view'), {'username': 'test_user', 'password': 'RDngdgssv@345'}).json().get('access')
        self.url = reverse('api-get_update_profile', args=[self.normal_user.pk])

    def test_get_user_profile_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
    
    def test_get_user_profile_inavalid_token(self):
        response = self.client.get(self.url, headers={'Authorization': f'Bearer invalid-token'})
        self.assertEqual(response.status_code, 401)

    def test_get_user_profile_authenticated(self):
        response = self.client.get(self.url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['id'], self.normal_user.pk)
        self.assertEqual(response.json()['user']['profile']['phone'], '0XXXX')
        self.assertEqual(response.json()['user']['profile']['address'], 'Jumuiya Road')
    
    def test_get_user_another_user_account_normal_user(self):
        response = self.client.get(reverse('api-get_update_profile', args=[self.admin.pk]), headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user not authorized to perform this action')

    def test_get_user_another_user_account_admin(self):
        response = self.client.get(self.url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['id'], self.normal_user.pk)
        self.assertEqual(response.json()['user']['profile']['phone'], '0XXXX')
        self.assertEqual(response.json()['user']['profile']['address'], 'Jumuiya Road')

    def test_get_unexisting_user(self):
        self.normal_user.profile.delete()
        response = self.client.get(self.url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'profile does not exist') 

    def test_update_user_profile_unauthenticated(self):
        response = self.client.patch(self.url, data={'first_name': 'updated_fn'})
        self.assertEqual(response.status_code, 401)
    
    def test_update_user_profile_inavalid_token(self):
        response = self.client.patch(self.url, data={'first_name': 'updated_fn'}, headers={'Authorization': f'Bearer invalid-token'})
        self.assertEqual(response.status_code, 401)

    def test_update_user_profile_authenticated(self):
        response = self.client.patch(self.url, data={'phone': '0123456789', 'address': 'Avenue Street'}, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.json()['user']['id'], self.normal_user.pk)
        self.assertEqual(response.json()['user']['profile']['phone'], '0123456789')
        self.assertEqual(response.json()['user']['profile']['address'], 'Avenue Street')
    
    def test_update_user_profile_another_user_account_normal_user(self):
        response = self.client.patch(reverse('api-update_user', args=[self.admin.pk]), data={'first_name': 'updated_fn'}, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)

    def test_update_user_profile_another_user_account_admin(self):
        response = self.client.patch(self.url, data={'phone': '0123456789', 'address': 'Avenue Street'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.json()['user']['id'], self.normal_user.pk)
        self.assertEqual(response.json()['user']['profile']['phone'], '0123456789')
        self.assertEqual(response.json()['user']['profile']['address'], 'Avenue Street')

    def test_update_unexisting_user_profile(self):
        self.normal_user.profile.delete()
        response = self.client.patch(self.url, data={'first_name': 'updated_fn'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'profile does not exist') 

    def test_delete_user_profile_unauthenticated(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)
    
    def test_delete_user_profile_inavalid_token(self):
        response = self.client.delete(self.url,headers={'Authorization': f'Bearer invalid_token'})
        self.assertEqual(response.status_code, 401)

    def test_delete_user_profile_authenticated(self):
        response = self.client.delete(self.url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'],'profile does not exist')

    
    def test_delete_user_profile_another_user_account_normal_user(self):
        response = self.client.delete(reverse('api-update_user', args=[self.admin.pk]), headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)

    def test_delete_user_profile_another_user_account_admin(self):
        response = self.client.delete(self.url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'],'profile does not exist')

    def test_delete_unexisting_user_profile(self):
        self.normal_user.profile.delete()
        response = self.client.delete(self.url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'profile does not exist')    

    
    # def test_user_buildings(self):
    #      response = self.client.get(self.__class__.profile_buildings_url, headers={'Authorization': f'Bearer {self.__class__.access_token}'})
    #      self.assertEqual(response.status_code, 200)
    #      self.assertEqual(len(response.json()['results']), 0)
    #      building1 = self.client.put(self.__class__.buildings_url, data={'user_id': self.__class__.user_id, 'building': '-4.5, 33.7'},  headers={'Authorization': f'Bearer {self.__class__.access_token}'})
    #      building2 = self.client.put(self.__class__.buildings_url, data={'user_id': self.__class__.user_id, 'building': '-2.6, 34.1'},  headers={'Authorization': f'Bearer {self.__class__.access_token}'})
    #      response = self.client.get(self.__class__.profile_buildings_url, headers={'Authorization': f'Bearer {self.__class__.access_token}'})
    #      self.assertEqual(response.status_code, 200)
    #      self.assertEqual(len(response.json()['results']), 2)
    
