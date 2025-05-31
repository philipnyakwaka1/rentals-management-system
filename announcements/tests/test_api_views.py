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
        cls.building = Building.objects.get(pk=cls.building_id)
        cls.tenant.profile.buildings.add(cls.building, through_defaults={'relationship': 'tenant'})
        cls.admin = User.objects.create_superuser(username='admin_user', password="Yyugbcdasdd@134")
        cls.admin_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'admin_user', 'password': "Yyugbcdasdd@134"}).json()['access']
    
    def test_create_comment_unauthenticated_user(self):
        data = {'tenant': self.tenant.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        response = self.client.put(self.create_get_url, data=data)
        self.assertEqual(response.status_code, 401)
    
    def test_create_comment_authenticated_user_not_linked_to_building(self):
        user = User.objects.create_user(username='user', password='Yyugbcdasdd@134')
        token = self.client.post(reverse('JWT-login_view'), data={'username': 'user', 'password': 'Yyugbcdasdd@134'}).json()['access']
        data = {'tenant': user.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        response = self.client.put(self.create_get_url, data=data, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile not linked to building')

    def test_create_comment_authenticated_user_not_tenant(self):
        data = {'tenant': self.owner.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        response = self.client.put(self.create_get_url, data=data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'cannot comment if not tenant')

    def test_create_comment_for_another_user(self):
        tenant_2 = User.objects.create_user(username='tenant_2', password='Yyugbcdasdd@134')
        tenant_2.profile.buildings.add(self.building, through_defaults={'relationship': 'tenant'})
        data = {'tenant': tenant_2.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        response = self.client.put(self.create_get_url, data=data, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user lacks necessary permissions')

    def test_create_comment_building_does_not_exist(self):
        data = {'tenant': self.tenant.pk, 'building': self.building_id + 1, 'comment': 'leaking roof'}
        response = self.client.put(self.create_get_url, data=data, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'building does not exist')
    
    def test_create_comment_authenticated_tenant(self):
        data = {'tenant': self.tenant.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        response = self.client.put(self.create_get_url, data=data, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 201)
    
    def test_get_all_comments_unauthenticated(self):
        response = self.client.get(self.create_get_url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user lacks permission to access this data')

    def test_get_all_comments_authenticated_user_not_admin(self):
        response = self.client.get(self.create_get_url, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user lacks permission to access this data')
    
    def test_get_all_comments_admin_user(self):
        response = self.client.get(self.create_get_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(len(response.json()['results']), 1)
        data = {'tenant': self.tenant.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        self.client.put(self.create_get_url, data=data, headers={'Authorization': f'Bearer {self.tenant_token}'})
        response = self.client.get(self.create_get_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(len(response.json()['results']), 2)
    
    def test_get_unexisting_comment(self):
        response = self.client.get(reverse('api-get_update_comment', args=[self.comment.pk + 1]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
    
    def test_get_existing_comment_unauthenticated(self):
        response = self.client.get(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 401)
    
    def test_get_existing_comment_authenticated_tenant(self):
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['pk'], self.comment.pk)
    
    def test_get_existing_comment_authenticated_not_tenant(self):
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_get_existing_comment_authenticated_admin_user(self):
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['pk'], self.comment.pk)
    
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
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.tenant_token}'})
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
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.admin_token}'})
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
        cls.building = Building.objects.get(pk=cls.building_id)
        cls.tenant.profile.buildings.add(cls.building, through_defaults={'relationship': 'tenant'})
        cls.admin = User.objects.create_superuser(username='admin_user', password="Yyugbcdasdd@134")
        cls.admin_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'admin_user', 'password': "Yyugbcdasdd@134"}).json()['access']
    
    def test_create_notice_unauthenticated_user(self):
        data = {'owner': self.owner.pk, 'building': self.building_id, 'notice': 'You have exhausted your deposit'}
        response = self.client.put(self.create_get_url, data=data)
        self.assertEqual(response.status_code, 401)

    def test_create_notice_authenticated_user_not_linked_to_building(self):
        user = User.objects.create_user(username='user', password='Yyugbcdasdd@178')
        token = self.client.post(reverse('JWT-login_view'), data={'username': 'user', 'password': 'Yyugbcdasdd@178'}).json()['access']
        response = self.client.put(self.create_get_url, data={'owner': user.pk, 'building': self.building_id, 'notice': 'rent is due'}, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile not linked to building')

    def test_create_notice_authenticated_user_is_tenant(self):
        response = self.client.put(self.create_get_url, data={'owner': self.tenant.pk, 'building': self.building_id, 'notice': 'rent is due'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'cannot create notice if not owner')
    
    def test_create_notice_for_another_user_authenticated_tenant(self):
        response = self.client.put(self.create_get_url, data={'owner': self.owner.pk, 'building': self.building_id, 'notice': 'rent is due'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have necessary permission')
    
    def test_create_notice_for_another_user_authenticated_owner(self):
        response = self.client.put(self.create_get_url, data={'owner': self.tenant.pk, 'building': self.building_id, 'notice': 'rent is due'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have necessary permission')
    
    def test_create_notice_for_nonexisting_building_authenticated_owner(self):
        response = self.client.put(self.create_get_url, data={'owner': self.owner.pk, 'building': self.building_id + 1, 'notice': 'rent is due'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'building does not exist')
    
    def test_create_notice_authenticated_owner(self):
        data = {'owner': self.owner.pk, 'building': self.building_id, 'notice': 'You have exhausted your deposit'}
        response = self.client.put(self.create_get_url, data=data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 201)

    def test_get_all_notices_unauthenticated_user(self):
        response = self.client.get(self.create_get_url)
        self.assertEqual(response.status_code, 403)

    def test_get_all_notices_user_not_admin(self):
        response = self.client.get(self.create_get_url, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)

    def test_get_all_notices_admin_user(self):
        response = self.client.get(self.create_get_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(len(response.json()['results']), 1)
        data = {'owner': self.owner.pk, 'building': self.building_id, 'notice': 'You have exhausted your deposit'}
        response = self.client.put(self.create_get_url, data=data, headers={'Authorization': f'Bearer {self.owner_token}'})
        response = self.client.get(self.create_get_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(len(response.json()['results']), 2)  

    def test_get_existing_notice_unauthenticated_user(self):
        response = self.client.get(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 403)
    
    def test_get_another_users_notice_authenticated_user_not_admin(self):
        self.tenant.profile.buildings.add(self.building, through_defaults={'relationship': 'owner'})
        notice = Notice.objects.create(owner=self.tenant, building=self.building, notice='rent is due')
        response = self.client.get(reverse('api-get_update_notice', args=[notice.pk]), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_get_another_users_notice_authenticated_admin(self):
        self.tenant.profile.buildings.add(self.building, through_defaults={'relationship': 'owner'})
        notice = Notice.objects.create(owner=self.tenant, building=self.building, notice='rent is due')
        response = self.client.get(reverse('api-get_update_notice', args=[notice.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
    
    def test_get_existing_notice_authenticated_owner(self):
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['pk'], self.notice.pk)
    
    def test_get_unexisting_notice(self):
        response = self.client.get(reverse('api-get_update_notice', args=[self.notice.pk + 1]), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 404)

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
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.owner_token}'})
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

