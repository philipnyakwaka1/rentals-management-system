from rest_framework.test import APITestCase
from users.api.v1 import views
from django.urls import reverse

class TestUserRegistration(APITestCase):

    def setUp(self):
        self.url = reverse('api-register_users')

    def test_succesful_create_account(self):
        response = self.client.put(self.url, {'username': 'nygma', 'password': 'Yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 201)
        self.assertTrue('id' in response.json().keys())
        self.assertTrue('username' in response.json().keys())

    def test_existing_username(self):
        user1_response = self.client.put(self.url, {'username': 'nygma', 'password': 'Yyugbcdasdd@134'})
        user2_response = self.client.put(self.url, {'username': 'nygma', 'password': 'Wyuxvbtdghsd@765'})
        self.assertEqual(user2_response.status_code, 400)
        self.assertEqual(user2_response.json()['error'], 'username already exists')

    def test_no_password(self):
        response = self.client.put(self.url, {'username': 'nygma'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': ['This field is required.']})

    def test_no_username(self):
        response = self.client.put(self.url, {'password': 'Yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'username': ['This field is required.']})

    def test_short_password(self):
        response = self.client.put(self.url, {'username': 'nygma', 'password': 'Yd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': {'error': ['password must be at least 8 characters long']}})

    def test_password_no_uppercase(self):
        response = self.client.put(self.url, {'username': 'nygma', 'password': 'yyugbcdasdd@134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': {'error': ['password must contain at least 1 uppercase character']}})

    def test_password_no_special(self):
        response = self.client.put(self.url, {'username': 'nygma', 'password': 'Yyugbcdasdd134'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': {'error': ['password must contain at least 1 special character']}})

    def test_password_no_number(self):
        response = self.client.put(self.url, {'username': 'nygma', 'password': 'Yyugbcdasdd@'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'password': {'error': ['password must contain at least 1 number']}})

    def test_password_all_criteria_fail(self):
        response = self.client.put(self.url, {'username': 'nygma', 'password': 'yy'})
        self.assertEqual(response.status_code, 400)
        self.assertTrue('password must be at least 8 characters long' in response.json()['password']['error'])
        self.assertTrue('password must contain at least 1 uppercase character' in response.json()['password']['error'])
        self.assertTrue('password must contain at least 1 special character' in response.json()['password']['error'])
        self.assertTrue('password must contain at least 1 number' in response.json()['password']['error'])
    