from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Profile, UserBuilding
from announcements.models import Notice
from buildings.models import Building
import math
from datetime import datetime



class TestUserRegistration(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api-user_register')

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
        cls.register_url = reverse('api-user_register')
        cls.login_url = reverse('api-user_login')
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

class TestLogout(APITestCase):
    pass

class TestAllUsers(APITestCase):

    @classmethod
    def setUpTestData(cls):
        for i in range(15):
            User.objects.create_user(username=f'test_user{i}', password=f'Tyugbcdasdd@134{i}')
        cls.admin = User.objects.create_superuser(username='admin_user', email='admin_user@gmail.com', password='Yyugbcdasdd@134')
        cls.normal_user = APIClient().put(reverse('api-user_register'), data={'username': 'test_user', 'password': 'RDngdgssv@345'})
        cls.admin_token = APIClient().post(reverse('api-user_login'), data={'username': 'admin_user', 'password': 'Yyugbcdasdd@134'}).json().get('access')
        cls.normal_token = APIClient().post(reverse('api-user_login'), data={'username': 'test_user', 'password': 'RDngdgssv@345'}).json().get('access')
        cls.users_list_url = reverse('api-users_list')
    
    def test_get_all_users_unauthenticated(self):
        response = APIClient().get(self.users_list_url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)

    def test_get_all_users_authenticated_not_admin(self):
        response = APIClient().get(self.users_list_url, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)

    def test_get_users_api_admin(self):
        response = APIClient().get(self.users_list_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        users = User.objects.all()
        self.assertEqual(len(response.json()['results']), 5)
        self.assertFalse(response.json()['previous'])
        self.assertTrue(response.json()['next'])
        total_pages = math.ceil(len(users) / 5)
        last_page = self.client.get(self.users_list_url + f'?page={total_pages}', headers={'Authorization': f'Bearer {self.admin_token}'}).json()
        self.assertTrue(last_page['previous'])
        self.assertFalse(last_page['next'])
        first_10_items = self.client.get(self.users_list_url + '?page=1&page_size=10', headers={'Authorization': f'Bearer {self.admin_token}'}).json()['results']
        self.assertEqual(len(first_10_items), 10)
        invalid_page = self.client.get(self.users_list_url + f'?page={total_pages + 1}', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(invalid_page.status_code, 404)


class TestUser(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('admin_user', 'admin_user@gmail.com', 'Yyugbcdasdd@134')
        cls.admin_token = APIClient().post(reverse('api-user_login'), {'username': 'admin_user', 'password': 'Yyugbcdasdd@134'}).json().get('access')
    
    def setUp(self):
        self.normal_user = User.objects.create_user(username='test_user', password='RDngdgssv@345')
        self.normal_token = APIClient().post(reverse('api-user_login'), {'username': 'test_user', 'password': 'RDngdgssv@345'}).json().get('access')
        self.url = reverse('api-user_retrieve_update', args=[self.normal_user.pk])

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
        response = self.client.get(reverse('api-user_retrieve_update', args=[self.admin.pk]), headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user not authorized to perform this action')

    def test_get_user_another_user_account_admin(self):
        response = self.client.get(self.url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.normal_user.pk)
        self.assertEqual(response.json()['username'], 'test_user')

    def test_get_unexisting_user(self):
        response = self.client.get(reverse('api-user_retrieve_update', args=[self.normal_user.pk + self.admin.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
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
        response = self.client.patch(reverse('api-user_retrieve_update', args=[self.admin.pk]), data={'first_name': 'updated_fn'}, headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)

    def test_update_user_another_user_account_admin(self):
        response = self.client.patch(self.url, data={'first_name': 'updated_fn'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(pk=self.normal_user.pk)
        self.assertEqual(user.first_name, 'updated_fn')

    def test_update_unexisting_user(self):
        response = self.client.patch(reverse('api-user_retrieve_update', args=[self.admin.pk + self.normal_user.pk]), data={'first_name': 'updated_fn'}, headers={'Authorization': f'Bearer {self.admin_token}'})
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
        response = self.client.put(reverse("api-building_list_create"), data={'user_id': self.normal_user.pk, 'building': '-4.5, 33.7'},  headers={'Authorization': f'Bearer {self.normal_token}'})
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
        response = self.client.delete(reverse('api-user_retrieve_update', args=[self.admin.pk]), headers={'Authorization': f'Bearer {self.normal_token}'})
        self.assertEqual(response.status_code, 403)

    def test_delete_user_another_user_account_admin(self):
        response = self.client.delete(self.url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.normal_user.pk)

    def test_delete_unexisting_user(self):
        response = self.client.delete(reverse('api-user_retrieve_update', args=[self.admin.pk + self.normal_user.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)        

class TestUserProfile(APITestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('admin_user', 'admin_user@gmail.com', 'Yyugbcdasdd@134')
        cls.admin_token = APIClient().post(reverse('api-user_login'), {'username': 'admin_user', 'password': 'Yyugbcdasdd@134'}).json().get('access')

    def setUp(self):
        self.normal_user = User.objects.create_user(username='test_user', password='RDngdgssv@345')
        self.normal_user.profile.phone = '0XXXX'
        self.normal_user.profile.address = 'Jumuiya Road'
        self.normal_user.profile.save()
        self.normal_token = APIClient().post(reverse('api-user_login'), {'username': 'test_user', 'password': 'RDngdgssv@345'}).json().get('access')
        self.url = reverse('api-profile_retrieve_update', args=[self.normal_user.pk])

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
        response = self.client.get(reverse('api-profile_retrieve_update', args=[self.admin.pk]), headers={'Authorization': f'Bearer {self.normal_token}'})
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
        response = self.client.patch(reverse('api-user_retrieve_update', args=[self.admin.pk]), data={'first_name': 'updated_fn'}, headers={'Authorization': f'Bearer {self.normal_token}'})
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
        response = self.client.delete(reverse('api-user_retrieve_update', args=[self.admin.pk]), headers={'Authorization': f'Bearer {self.normal_token}'})
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




class TestBuildingUserProfiles(APITestCase):

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

    def setUp(self):
        data = {
            'user_id': self.owner.pk,
            'building': '-4.0, 32.5',
        }
        response = self.client.put(reverse("api-building_list_create"), data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.building = Building.objects.get(pk=response.json().get('id'))
        self.tenant.profile.buildings.add(self.building, through_defaults={'relationship': 'tenant'})
        self.building_profiles_list_url = reverse("api-users_list_by_building", args=[self.building.pk])
        self.building_profile_add_url = reverse('api-profile_add_to_building', args=[self.building.pk])
        self.building_profile_delete_url = reverse('api-profile_remove_from_building', args=[self.building.pk, self.regular_user.pk])
    
    def test_list_building_users_fails_when_unauthenticated(self):
        response = self.client.get(self.building_profiles_list_url)
        self.assertEqual(response.status_code, 401)

    def test_list_building_users_fails_for_unlinked_user(self):
        response = self.client.get(self.building_profiles_list_url, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile not linked to building')

    def test_list_building_users_succeeds_for_admin(self):
        response = self.client.get(self.building_profiles_list_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 2)
        user_ids = list(map(lambda x: x['user']['id'], response.json()['results']))
        self.assertTrue(self.owner.pk in user_ids)
        self.assertTrue(self.tenant.pk in user_ids)
    
    def test_list_building_users_succeeds_for_tenant(self):
        response = self.client.get(self.building_profiles_list_url, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 2)
        user_ids = list(map(lambda x: x['user']['id'], response.json()['results']))
        self.assertTrue(self.owner.pk in user_ids)
        self.assertTrue(self.tenant.pk in user_ids)
    
    def test_list_building_users_succeeds_for_owner(self):
        response = self.client.get(self.building_profiles_list_url, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 2)
        user_ids = list(map(lambda x: x['user']['id'], response.json()['results']))
        self.assertTrue(self.owner.pk in user_ids)
        self.assertTrue(self.tenant.pk in user_ids)

    def test_filter_tenants_fails_for_unlinked_user(self):
        response = self.client.get(self.building_profiles_list_url, data={'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile not linked to building')

    def test_filter_owners_fails_for_unlinked_user(self):
        response = self.client.get(self.building_profiles_list_url, data={'relationship': 'owner'}, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile not linked to building')

    def test_filter_tenants_succeeds_for_linked_users_or_admin(self):
        response = self.client.get(self.building_profiles_list_url, data={'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.tenant.pk)
        response = self.client.get(self.building_profiles_list_url, data={'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.tenant.pk)
        response = self.client.get(self.building_profiles_list_url, data={'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.tenant.pk)

    def test_filter_owners_succeeds_for_linked_users_or_admin(self):
        response = self.client.get(self.building_profiles_list_url, data={'relationship': 'owner'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.owner.pk)
        response = self.client.get(self.building_profiles_list_url, data={'relationship': 'owner'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.owner.pk)
        response = self.client.get(self.building_profiles_list_url, data={'relationship': 'owner'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['user']['id'], self.owner.pk)
    
    def test_add_profile_fails_when_unauthenticated(self):
        response = self.client.patch(self.building_profile_add_url, data={'user_id': self.regular_user.pk, 'relationship': 'tenant'})
        self.assertEqual(response.status_code, 401)
    
    def test_add_profile_fails_for_tenant_user(self):
        response = self.client.patch(self.building_profile_add_url, data={'user_id': self.regular_user.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building')
    
    def test_add_profile_fails_for_unlinked_user(self):
        response = self.client.patch(self.building_profile_add_url, data={'user_id': self.regular_user.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building, profile not linked to building')
    
    def  test_add_profile_succeeds_for_admin(self):
        response = self.client.patch(self.building_profile_add_url, data={'user_id': self.regular_user.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        building_profile = UserBuilding.objects.get(profile=self.regular_user.profile, building=self.building)
        self.assertEqual(building_profile.profile, self.regular_user.profile)
        self.assertEqual(building_profile.relationship, 'tenant')
        response = self.client.get(self.building_profiles_list_url, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 3)
        user_ids = list(map(lambda x: x['user']['id'], response.json()['results']))
        self.assertTrue(self.regular_user.pk in user_ids)
    
    def test_add_profile_succeeds_for_owner(self):
        response = self.client.patch(self.building_profile_add_url, data={'user_id': self.regular_user.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        building_profile = UserBuilding.objects.get(profile=self.regular_user.profile, building=self.building)
        self.assertEqual(building_profile.profile, self.regular_user.profile)
        self.assertEqual(building_profile.relationship, 'tenant')
        response = self.client.get(self.building_profiles_list_url, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 3)
        user_ids = list(map(lambda x: x['user']['id'], response.json()['results']))
        self.assertTrue(self.regular_user.pk in user_ids)
        
    
    def test_add_profile_fails_missing_relationship_key(self):
        response = self.client.patch(self.building_profile_add_url, data={'user_id': self.regular_user.pk}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'must provide user id and relationship to building')
    
    def test_add_profile_fails_missing_user_id(self):
        response = self.client.patch(self.building_profile_add_url, data={'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'must provide user id and relationship to building')

    def test_add_profile_fails_for_user_with_no_profile(self):
        self.tenant.profile.delete()
        response = self.client.patch(self.building_profile_add_url, data={'user_id': self.tenant.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'user profile does not exist')
    
    def test_add_profile_fails_for_nonexistent_user(self):
        self.tenant.profile.delete()
        response = self.client.patch(self.building_profile_add_url, data={'user_id': self.tenant.pk + self.regular_user.pk + self.owner.pk + self.admin.pk, 'relationship': 'tenant'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'user does not exist')
    
    def test_remove_profile_fails_when_unauthenticated(self):
        response = self.client.delete(self.building_profile_delete_url)
        self.assertEqual(response.status_code, 401)

    def test_remove_profile_fails_for_tenant_user(self):
        self.regular_user.profile.buildings.add(self.building, through_defaults={'relationship': 'tenant'})
        response = self.client.delete(self.building_profile_delete_url, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have permission to modify this building')

    def test_remove_profile_succeeds_for_admin_user(self):
        self.regular_user.profile.buildings.add(self.building, through_defaults={'relationship': 'tenant'})
        response = self.client.delete(self.building_profile_delete_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(UserBuilding.DoesNotExist):
            UserBuilding.objects.get(profile=self.regular_user.profile, building=self.building)

    def test_remove_profile_succeeds_for_owner_user(self):
        self.regular_user.profile.buildings.add(self.building, through_defaults={'relationship': 'tenant'})
        response = self.client.delete(self.building_profile_delete_url, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(UserBuilding.DoesNotExist):
            UserBuilding.objects.get(profile=self.regular_user.profile, building=self.building)

    def test_remove_user_from_building_and_prevent_only_owner_removal(self):
        self.regular_user.profile.buildings.add(self.building, through_defaults={'relationship': 'owner'})
        response = self.client.delete(reverse('api-profile_remove_from_building', args=[self.building.pk, self.regular_user.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(UserBuilding.DoesNotExist):
            UserBuilding.objects.get(profile=self.regular_user.profile, building=self.building)
        response = self.client.delete(reverse('api-profile_remove_from_building', args=[self.building.pk, self.owner.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'cannot delete building only owner')
        user_building = UserBuilding.objects.get(profile=self.owner.profile, building=self.building)
        self.assertEqual(self.owner.profile, user_building.profile)

    
    
