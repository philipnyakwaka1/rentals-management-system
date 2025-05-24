from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from announcements.models import Comment, Notice
from buildings.models import Building
from django.urls import reverse

class TestComments(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tenant = User.objects.create_user(username='test_tenant', password='Yyugbcdasdd@134')
        cls.tenant_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'test_tenant', 'password': 'Yyugbcdasdd@134'}).json()['access']
        cls.owner = User.objects.create_user(username='test_owner', password='Yyugbcdasdd@178')
        cls.owner_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'test_owner', 'password': 'Yyugbcdasdd@178'}).json()['access']
        cls.building_id = APIClient().put(reverse('api-create_query_building'), data={'user_id': cls.owner.pk, 'building': '-4.0, 33.1'}, headers={'Authorization': f'Bearer {cls.owner_token}'}).json()['id']
        cls.create_get_url = reverse('api-create_get_comment')
        cls.comment = Comment.objects.create(tenant=cls.tenant, building=Building.objects.get(pk=cls.building_id), comment='tap has no water')
        cls.get_update_delete_urls = reverse('api-get_update_comment', args=[cls.comment.pk])
    
    def test_create_comment_unauthenticated_user(self):
        data = {'tenant': self.tenant.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        response = self.client.put(self.create_get_url, data=data)
        self.assertEqual(response.status_code, 401)

    def test_create_comment_authenticated_user(self):
        data = {'tenant': self.tenant.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        response = self.client.put(self.create_get_url, data=data, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 201)
    
    def test_get_unexisting_comment(self):
        response = self.client.get(reverse('api-get_update_comment', args=[self.comment.pk + 1]))
        self.assertEqual(response.status_code, 404)
    
    def test_get_existing_comment(self):
        response = self.client.get(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['pk'], self.comment.pk)
    
    def test_get_all_comments(self):
        response = self.client.get(self.create_get_url)
        self.assertEqual(len(response.json()['results']), 1)
        data = {'tenant': self.tenant.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        self.client.put(self.create_get_url, data=data, headers={'Authorization': f'Bearer {self.tenant_token}'})
        response = self.client.get(self.create_get_url)
        self.assertEqual(len(response.json()['results']), 2)
    
    def test_update_comment_unauthenticated_user(self):
        response = self.client.patch(self.get_update_delete_urls, data={'comment': 'edited comment'})
        self.assertEqual(response.status_code, 401)
    
    def test_update_another_users_comment(self):
        response = self.client.patch(self.get_update_delete_urls, data={'comment': 'edited comment'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_update_comment_tenant(self):
        response = self.client.patch(self.get_update_delete_urls, data={'comment': 'edited comment', 'tenant': self.owner.pk}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 400)
    
    def test_update_comment_building(self):
        response = self.client.patch(self.get_update_delete_urls, data={'comment': 'edited comment', 'building': self.building_id}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 400)
    
    def test_update_comment_tenant_and_building(self):
        response = self.client.patch(self.get_update_delete_urls, data={'comment': 'edited comment', 'building': self.building_id,'tenant': self.owner.pk}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 400)
    
    def test_update_comment_text(self):
        response = self.client.patch(self.get_update_delete_urls, data={'comment': 'edited comment'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.get_update_delete_urls)
        self.assertEqual(response.json()['comment'], 'edited comment')
        
    
    def test_delete_comment_unauthenticated_user(self):
        response = self.client.delete(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 401)
    
    def test_delete_another_users_comment(self):
        response = self.client.delete(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_delete_unexisting_comment(self):
        response = self.client.delete(reverse('api-get_update_comment', args=[self.comment.pk + 1]), headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 404)
    
    def test_delete_comment(self):
        response = self.client.delete(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 404)


class TestNotices(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tenant = User.objects.create_user(username='test_tenant', password='Yyugbcdasdd@134')
        cls.tenant_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'test_tenant', 'password': 'Yyugbcdasdd@134'}).json()['access']
        cls.owner = User.objects.create_user(username='test_owner', password='Yyugbcdasdd@178')
        cls.owner_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'test_owner', 'password': 'Yyugbcdasdd@178'}).json()['access']
        cls.building_id = APIClient().put(reverse('api-create_query_building'), data={'user_id': cls.owner.pk, 'building': '-4.0, 33.1'}, headers={'Authorization': f'Bearer {cls.owner_token}'}).json()['id']
        cls.create_get_url = reverse('api-create_get_notice')
        cls.notice = Notice.objects.create(owner=cls.owner, building=Building.objects.get(pk=cls.building_id), notice='rent is due')
        cls.get_update_delete_urls = reverse('api-get_update_notice', args=[cls.notice.pk])
    
    def test_create_notice_unauthenticated_user(self):
        data = {'owner': self.owner.pk, 'building': self.building_id, 'notice': 'You have exhausted your deposit'}
        response = self.client.put(self.create_get_url, data=data)
        self.assertEqual(response.status_code, 401)

    def test_create_notice_authenticated_user(self):
        data = {'owner': self.owner.pk, 'building': self.building_id, 'notice': 'You have exhausted your deposit'}
        response = self.client.put(self.create_get_url, data=data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 201)
    
    def test_get_unexisting_notice(self):
        response = self.client.get(reverse('api-get_update_notice', args=[self.notice.pk + 1]))
        self.assertEqual(response.status_code, 404)
    
    def test_get_existing_notice(self):
        response = self.client.get(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['pk'], self.notice.pk)
    
    def test_get_all_notices(self):
        response = self.client.get(self.create_get_url)
        self.assertEqual(len(response.json()['results']), 1)
        data = {'owner': self.owner.pk, 'building': self.building_id, 'notice': 'You have exhausted your deposit'}
        self.client.put(self.create_get_url, data=data, headers={'Authorization': f'Bearer {self.owner_token}'})
        response = self.client.get(self.create_get_url)
        self.assertEqual(len(response.json()['results']), 2)
    
    def test_update_notice_unauthenticated_user(self):
        response = self.client.patch(self.get_update_delete_urls, data={'notice': 'edited notice'})
        self.assertEqual(response.status_code, 401)
    
    def test_update_another_users_notice(self):
        response = self.client.patch(self.get_update_delete_urls, data={'notice': 'edited notice'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_update_notice_owner(self):
        response = self.client.patch(self.get_update_delete_urls, data={'notice': 'edited notice', 'owner': self.tenant.pk}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
    
    def test_update_notice_building(self):
        response = self.client.patch(self.get_update_delete_urls, data={'notice': 'edited notice', 'building': self.building_id}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
    
    def test_update_notice_owner_and_building(self):
        response = self.client.patch(self.get_update_delete_urls, data={'notice': 'edited notice', 'building': self.building_id,'owner': self.tenant.pk}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
    
    def test_update_notice_text(self):
        response = self.client.patch(self.get_update_delete_urls, data={'notice': 'edited notice'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.get_update_delete_urls)
        self.assertEqual(response.json()['notice'], 'edited notice')
        
    
    def test_delete_notice_unauthenticated_user(self):
        response = self.client.delete(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 401)
    
    def test_delete_another_users_notice(self):
        response = self.client.delete(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_delete_unexisting_notice(self):
        response = self.client.delete(reverse('api-get_update_notice', args=[self.notice.pk + 1]), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 404)
    
    def test_delete_notice(self):
        response = self.client.delete(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 404)

