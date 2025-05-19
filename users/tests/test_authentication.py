from django.test import override_settings
from rest_framework.test import APIClient, APITestCase
from datetime import timedelta
from django.urls import reverse
import time

class TestAuthenticationTokens(APITestCase):
    """
    Settings.py file is modified during this test.
    Access token lifetime is set to 2 seconds
    Refresh token lifetime is set to 5 seconds
    """
    @override_settings(SIMPLE_JWT = 
    {"ACCESS_TOKEN_LIFETIME": timedelta(seconds=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(seconds=5),
    "ROTATE_REFRESH_TOKENS": False
    })
    def setUp(self):
        self.register_url = reverse('api-register_users')
        self.login_url = reverse('JWT-login_view')
        self.user_register_response = self.client.put(self.register_url, {'username': 'test_user', 'password': 'Yyugbcdasdd@134'})
        self.user_id = self.user_register_response.json()['id']
        self.user_data_url = reverse('api-update_user', args=[self.user_id])
        self.response_login = self.client.post(self.login_url, {'username': 'test_user', 'password': 'Yyugbcdasdd@134'})
        self.access_token = self.response_login.json()['access']
    
    def test_authenticated_access_valid_token(self):
        response_401 = self.client.get(self.user_data_url)
        self.assertEqual(response_401.status_code, 401)
        response_200 = self.client.get(self.user_data_url, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response_200.status_code, 200)
        self.assertEqual(response_200.json()['username'], 'test_user')

    def test_expired_tokens(self):
        response_login = self.client.post(self.login_url, {'username': 'test_user', 'password': 'Yyugbcdasdd@134'})
        access_token = response_login.json()['access']
        response_200 = self.client.get(self.user_data_url, headers={'Authorization': f'Bearer {access_token}'})
        self.assertEqual(response_200.status_code, 200)
        time.sleep(2)
        response_401 = self.client.get(self.user_data_url, headers={'Authorization': f'Bearer {access_token}'})
        self.assertEqual(response_401.status_code, 401)
    
    def test_refresh_token(self):
        clientB = APIClient()
        response_login = clientB.post(self.login_url, {'username': 'test_user', 'password': 'Yyugbcdasdd@134'})
        access_token = response_login.json()['access']
        response_200 = clientB.get(self.user_data_url, headers={'Authorization': f'Bearer {access_token}'})
        self.assertEqual(response_200.status_code, 200)
        time.sleep(2)
        response_401 = clientB.get(self.user_data_url, headers={'Authorization': f'Bearer {access_token}'})
        self.assertEqual(response_401.status_code, 401)
        response_refresh_token = clientB.get(reverse('refresh_token'))
        new_access_token = response_refresh_token.json()['access']
        response_200 = clientB.get(self.user_data_url, headers={'Authorization': f'Bearer {new_access_token}'})
        self.assertEqual(response_200.status_code, 200)
    
    def test_expired_refresh_token(self):
        time.sleep(5)
        response_401 = self.client.get(self.user_data_url, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response_401.status_code, 401)
        response_refresh_token_403 = self.client.get(reverse('refresh_token'))
        self.assertEqual(response_refresh_token_403.status_code, 403)
    
    def test_invalid_refresh_token(self):
        self.client.cookies['refresh_token'] = 'invalid_refresh_token'
        response1_refresh_token_400 = self.client.get(reverse('refresh_token'))
        self.assertEqual(response1_refresh_token_400.status_code, 403)
        self.assertTrue(self.client.cookies.get('refresh_token'))
        self.client.cookies.clear()
        self.assertFalse(self.client.cookies.get('refresh_token'))
        response2_refresh_token_400 = self.client.get(reverse('refresh_token'))
        self.assertEqual(response2_refresh_token_400.status_code, 400)

    def test_logout(self):
        response_logout = self.client.get(reverse('logout_user'))
        response_refresh_token_400 = self.client.get(reverse('refresh_token'))
        self.assertEqual(response_refresh_token_400.status_code, 400)