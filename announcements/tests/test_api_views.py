from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from announcements.models import Comment, Notice
from buildings.models import Building
from django.urls import reverse

class TestComments(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.regular_user = User.objects.create_user(username='regular_user', password='Gyuxxcdasdd@579')
        cls.regular_user_token = APIClient().post(reverse('JWT-login_view'), {'username': 'regular_user', 'password': 'Gyuxxcdasdd@579'}).json().get('access')
        cls.tenant = User.objects.create_user(username='test_tenant', password='Yyugbcdasdd@134')
        cls.tenant_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'test_tenant', 'password': 'Yyugbcdasdd@134'}).json()['access']
        cls.owner = User.objects.create_user(username='test_owner', password='Yyugbcdasdd@178')
        cls.owner_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'test_owner', 'password': 'Yyugbcdasdd@178'}).json()['access']
        cls.building_id = APIClient().put(reverse('api-create_query_building'), data={'user_id': cls.owner.pk, 'building': '-4.0, 33.1'}, headers={'Authorization': f'Bearer {cls.owner_token}'}).json()['id']
        cls.list_create_url = reverse('api_comment_list_create')
        cls.list_building_comments_url = reverse('api_comment_list_by_building', args=[cls.building_id])
        cls.list_user_comments_url = reverse('api_comment_list_by_user', args=[cls.tenant.pk])
        cls.building = Building.objects.get(pk=cls.building_id)
        cls.tenant.profile.buildings.add(cls.building, through_defaults={'relationship': 'tenant'})
        cls.admin = User.objects.create_superuser(username='admin_user', password="Yyugbcdasdd@134")
        cls.admin_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'admin_user', 'password': "Yyugbcdasdd@134"}).json()['access']
    
    def setUp(self):
        self.comment = Comment.objects.create(tenant=self.tenant, building=self.building, comment='tap has no water')
        self.get_update_delete_urls = reverse('api_comment_retrieve_update', args=[self.comment.pk])
    
    def create_building_comments(self):
        comment1 = Comment.objects.create(tenant=self.tenant, building=self.building, comment='leaking roof')
        comment2 = Comment.objects.create(tenant=self.tenant, building=self.building, comment='door knob is broken')
        return (comment1, comment2)

    def test_put_comment_fails_for_unauthenticated_user(self):
        data = {'tenant': self.tenant.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        response = self.client.put(self.list_create_url, data=data)
        self.assertEqual(response.status_code, 401)
    
    def test_put_comment_fails_when_user_not_linked_to_building(self):
        user = User.objects.create_user(username='user', password='Yyugbcdasdd@134')
        token = self.client.post(reverse('JWT-login_view'), data={'username': 'user', 'password': 'Yyugbcdasdd@134'}).json()['access']
        data = {'tenant': user.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        response = self.client.put(self.list_create_url, data=data, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile not linked to building')

    def test_put_comment_fails_when_user_is_not_tenant(self):
        data = {'tenant': self.owner.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        response = self.client.put(self.list_create_url, data=data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'cannot comment if not tenant')

    def test_put_comment_fails_when_user_comments_on_behalf_of_another(self):
        tenant_2 = User.objects.create_user(username='tenant_2', password='Yyugbcdasdd@134')
        tenant_2.profile.buildings.add(self.building, through_defaults={'relationship': 'tenant'})
        data = {'tenant': tenant_2.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        response = self.client.put(self.list_create_url, data=data, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user lacks necessary permissions')

    def test_put_comment_fails_when_building_does_not_exist(self):
        data = {'tenant': self.tenant.pk, 'building': self.building_id + 1, 'comment': 'leaking roof'}
        response = self.client.put(self.list_create_url, data=data, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'building does not exist')
    
    def test_put_comment_succeeds_for_authenticated_tenant(self):
        data = {'tenant': self.tenant.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        response = self.client.put(self.list_create_url, data=data, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 201)
    
    def test_get_comments_fails_for_unauthenticated_user(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user lacks permission to access this data')

    def test_get_comments_fails_for_non_admin_user(self):
        response = self.client.get(self.list_create_url, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user lacks permission to access this data')
    
    def test_get_comments_succeeds_for_admin_user(self):
        response = self.client.get(self.list_create_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(len(response.json()['results']), 1)
        data = {'tenant': self.tenant.pk, 'building': self.building_id, 'comment': 'leaking roof'}
        self.client.put(self.list_create_url, data=data, headers={'Authorization': f'Bearer {self.tenant_token}'})
        response = self.client.get(self.list_create_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(len(response.json()['results']), 2)
    
    def test_get_comment_fails_for_nonexistent_comment(self):
        response = self.client.get(reverse('api_comment_retrieve_update', args=[self.comment.pk + 1]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
    
    def test_get_comment_fails_for_unauthenticated_user(self):
        response = self.client.get(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 401)
    
    def test_get_comment_succeeds_for_authenticated_tenant(self):
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['pk'], self.comment.pk)
    
    def test_get_comment_fails_for_authenticated_non_tenant(self):
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_get_comment_succeeds_for_admin_user(self):
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['pk'], self.comment.pk)
    
    def test_update_comment_fails_for_unauthenticated_user(self):
        response = self.client.patch(self.get_update_delete_urls, data={'comment': 'edited comment'})
        self.assertEqual(response.status_code, 401)
    
    def test_update_comment_fails_for_non_owner_user(self):
        response = self.client.patch(self.get_update_delete_urls, data={'comment': 'edited comment'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_update_comment_fails_when_changing_tenant_field(self):
        response = self.client.patch(self.get_update_delete_urls, data={'comment': 'edited comment', 'tenant': self.owner.pk}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 400)
    
    def test_update_comment_fails_when_changing_building_field(self):
        response = self.client.patch(self.get_update_delete_urls, data={'comment': 'edited comment', 'building': self.building_id}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 400)
    
    def test_update_comment_fails_when_changing_tenant_and_building_fields(self):
        response = self.client.patch(self.get_update_delete_urls, data={'comment': 'edited comment', 'building': self.building_id,'tenant': self.owner.pk}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 400)
    
    def test_update_comment_succeeds_when_editing_text_only(self):
        response = self.client.patch(self.get_update_delete_urls, data={'comment': 'edited comment'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.json()['comment'], 'edited comment')
        
    def test_delete_comment_fails_for_unauthenticated_user(self):
        response = self.client.delete(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 401)
    
    def test_delete_comment_fails_for_non_owner_user(self):
        response = self.client.delete(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_delete_comment_fails_for_nonexistent_comment(self):
        response = self.client.delete(reverse('api_comment_retrieve_update', args=[self.comment.pk + 1]), headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 404)
    
    def test_delete_comment_succeeds_for_owner_user(self):
        response = self.client.delete(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
    
    def test_list_building_comments_fails_for_unauthenticated_user(self):
        response = self.client.get(self.list_building_comments_url)
        self.assertEqual(response.status_code, 401)

    def test_list_building_comments_fails_for_user_not_linked_to_building(self):
        response = self.client.get(self.list_building_comments_url, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile not linked to building')

    def test_list_building_comments_succeeds_for_tenant_user(self):
        comments = self.create_building_comments()
        response = self.client.get(self.list_building_comments_url, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        all_comments_ids = list(map(lambda x: x['pk'], response.json()['results']))
        self.assertEqual(len(all_comments_ids), 3)
        self.assertTrue(self.comment.pk in all_comments_ids and comments[0].pk in all_comments_ids and comments[1].pk in all_comments_ids)

    def test_list_building_comments_succeeds_for_owner_user(self):
        comments = self.create_building_comments()
        response = self.client.get(self.list_building_comments_url, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        all_comments_ids = list(map(lambda x: x['pk'], response.json()['results']))
        self.assertEqual(len(all_comments_ids), 3)
        self.assertTrue(self.comment.pk in all_comments_ids and comments[0].pk in all_comments_ids and comments[1].pk in all_comments_ids)

    def test_list_building_comments_succeeds_for_admin_user(self):
        comments = self.create_building_comments()
        response = self.client.get(self.list_building_comments_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        all_comments_ids = list(map(lambda x: x['pk'], response.json()['results']))
        self.assertEqual(len(all_comments_ids), 3)
        self.assertTrue(self.comment.pk in all_comments_ids and comments[0].pk in all_comments_ids and comments[1].pk in all_comments_ids)
    
    def test_list_building_comments_fails_for_nonexistent_building(self):
        response = self.client.get(reverse('api_comment_list_by_building', args=[self.building_id + 1]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'Building does not exist')

    def test_list_user_comments_fails_for_unauthenticated_user(self):
        response = self.client.get(self.list_user_comments_url)
        self.assertEqual(response.status_code, 401)

    def test_list_user_comments_fails_for_user_attempting_to_access_another_user_comments(self):
        response = self.client.get(self.list_user_comments_url, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'permission denied')

    def test_list_user_comments_succeeds_for_admin_accessing_own_comments(self):
        comments = self.create_building_comments()
        response = self.client.get(self.list_user_comments_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        all_comments_ids = list(map(lambda x: x['pk'], response.json()['results']))
        self.assertEqual(len(all_comments_ids), 3)
        self.assertTrue(self.comment.pk in all_comments_ids and comments[0].pk in all_comments_ids and comments[1].pk in all_comments_ids)
        response = self.client.get(reverse('api_comment_list_by_user', args=[self.admin.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.json()['results'], [])
    

    def test_list_user_comments_succeeds_for_authenticated_user(self):
        comments = self.create_building_comments()
        response = self.client.get(self.list_user_comments_url, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        all_comments_ids = list(map(lambda x: x['pk'], response.json()['results']))
        self.assertEqual(len(all_comments_ids), 3)
        self.assertTrue(self.comment.pk in all_comments_ids and comments[0].pk in all_comments_ids and comments[1].pk in all_comments_ids)

    def test_list_user_comments_fails_for_nonexistent_user(self):
        response = self.client.get(reverse('api_comment_list_by_user', args=[self.tenant.pk + self.admin.pk + self.regular_user.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'user does not exist')



class TestNotices(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.regular_user = User.objects.create_user(username='regular_user', password='Gyuxxcdasdd@579')
        cls.regular_user_token = APIClient().post(reverse('JWT-login_view'), {'username': 'regular_user', 'password': 'Gyuxxcdasdd@579'}).json().get('access')
        cls.tenant = User.objects.create_user(username='test_tenant', password='Yyugbcdasdd@134')
        cls.tenant_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'test_tenant', 'password': 'Yyugbcdasdd@134'}).json()['access']
        cls.owner = User.objects.create_user(username='test_owner', password='Yyugbcdasdd@178')
        cls.owner_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'test_owner', 'password': 'Yyugbcdasdd@178'}).json()['access']
        cls.building_id = APIClient().put(reverse('api-create_query_building'), data={'user_id': cls.owner.pk, 'building': '-4.0, 33.1'}, headers={'Authorization': f'Bearer {cls.owner_token}'}).json()['id']
        cls.list_create_url = reverse('api_notice_list_create')
        cls.list_building_notices_url = reverse('api_notice_list_by_building', args=[cls.building_id])
        cls.list_user_notices_url = reverse('api_notice_list_by_user', args=[cls.owner.pk])
        cls.building = Building.objects.get(pk=cls.building_id)
        cls.tenant.profile.buildings.add(cls.building, through_defaults={'relationship': 'tenant'})
        cls.admin = User.objects.create_superuser(username='admin_user', password="Yyugbcdasdd@134")
        cls.admin_token = APIClient().post(reverse('JWT-login_view'), data={'username': 'admin_user', 'password': "Yyugbcdasdd@134"}).json()['access']

    def setUp(self):
        self.notice = Notice.objects.create(owner=self.owner, building=self.building, notice='rent is due')
        self.get_update_delete_urls = reverse('api_notice_retrieve_update', args=[self.notice.pk])

    def create_building_notices(self):
        notice1 = Notice.objects.create(owner=self.owner, building=self.building, notice='rent is due')
        notice2 = Notice.objects.create(owner=self.owner, building=self.building, notice='you exhausted your deposit')
        return (notice1, notice2)

    def test_create_notice_fails_for_unauthenticated_user(self):
        data = {'owner': self.owner.pk, 'building': self.building_id, 'notice': 'You have exhausted your deposit'}
        response = self.client.put(self.list_create_url, data=data)
        self.assertEqual(response.status_code, 401)

    def test_create_notice_fails_if_user_not_linked_to_building(self):
        user = User.objects.create_user(username='user', password='Yyugbcdasdd@178')
        token = self.client.post(reverse('JWT-login_view'), data={'username': 'user', 'password': 'Yyugbcdasdd@178'}).json()['access']
        response = self.client.put(self.list_create_url, data={'owner': user.pk, 'building': self.building_id, 'notice': 'rent is due'}, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile not linked to building')

    def test_create_notice_fails_if_authenticated_user_is_tenant(self):
        response = self.client.put(self.list_create_url, data={'owner': self.tenant.pk, 'building': self.building_id, 'notice': 'rent is due'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'cannot create notice if not owner')
    
    def test_create_notice_fails_when_tenant_creates_notice_for_another_user(self):
        response = self.client.put(self.list_create_url, data={'owner': self.owner.pk, 'building': self.building_id, 'notice': 'rent is due'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have necessary permission')
    
    def test_create_notice_fails_when_owner_creates_notice_for_another_user(self):
        response = self.client.put(self.list_create_url, data={'owner': self.tenant.pk, 'building': self.building_id, 'notice': 'rent is due'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user does not have necessary permission')
    
    def test_create_notice_fails_for_nonexistent_building(self):
        response = self.client.put(self.list_create_url, data={'owner': self.owner.pk, 'building': self.building_id + 1, 'notice': 'rent is due'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'building does not exist')
    
    def test_create_notice_succeeds_for_authenticated_owner(self):
        data = {'owner': self.owner.pk, 'building': self.building_id, 'notice': 'You have exhausted your deposit'}
        response = self.client.put(self.list_create_url, data=data, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 201)

    def test_get_all_notices_fails_for_unauthenticated_user(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, 403)

    def test_get_all_notices_fails_for_non_admin_user(self):
        response = self.client.get(self.list_create_url, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)

    def test_get_all_notices_succeeds_for_admin_user(self):
        response = self.client.get(self.list_create_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(len(response.json()['results']), 1)
        data = {'owner': self.owner.pk, 'building': self.building_id, 'notice': 'You have exhausted your deposit'}
        response = self.client.put(self.list_create_url, data=data, headers={'Authorization': f'Bearer {self.owner_token}'})
        response = self.client.get(self.list_create_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(len(response.json()['results']), 2)  

    def test_get_existing_notice_fails_for_unauthenticated_user(self):
        response = self.client.get(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 403)
    
    def test_get_another_users_notice_fails_for_authenticated_non_admin_user(self):
        self.tenant.profile.buildings.add(self.building, through_defaults={'relationship': 'owner'})
        notice = Notice.objects.create(owner=self.tenant, building=self.building, notice='rent is due')
        response = self.client.get(reverse('api_notice_retrieve_update', args=[notice.pk]), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_get_another_users_notice_succeeds_for_authenticated_admin_user(self):
        self.tenant.profile.buildings.add(self.building, through_defaults={'relationship': 'owner'})
        notice = Notice.objects.create(owner=self.tenant, building=self.building, notice='rent is due')
        response = self.client.get(reverse('api_notice_retrieve_update', args=[notice.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
    
    def test_get_existing_notice_succeeds_for_authenticated_owner(self):
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['pk'], self.notice.pk)
    
    def test_get_notice_fails_for_nonexistent_notice(self):
        response = self.client.get(reverse('api_notice_retrieve_update', args=[self.notice.pk + 1]), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 404)

    def test_update_notice_fails_for_unauthenticated_user(self):
        response = self.client.patch(self.get_update_delete_urls, data={'notice': 'edited notice'})
        self.assertEqual(response.status_code, 401)
    
    def test_update_notice_fails_for_non_owner_user(self):
        response = self.client.patch(self.get_update_delete_urls, data={'notice': 'edited notice'}, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_update_notice_fails_when_changing_owner_field(self):
        response = self.client.patch(self.get_update_delete_urls, data={'notice': 'edited notice', 'owner': self.tenant.pk}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
    
    def test_update_notice_fails_when_changing_building_field(self):
        response = self.client.patch(self.get_update_delete_urls, data={'notice': 'edited notice', 'building': self.building_id}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
    
    def test_update_notice_fails_when_changing_owner_and_building_fields(self):
        response = self.client.patch(self.get_update_delete_urls, data={'notice': 'edited notice', 'building': self.building_id,'owner': self.tenant.pk}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 400)
    
    def test_update_notice_succeeds_when_updating_notice_text_only(self):
        response = self.client.patch(self.get_update_delete_urls, data={'notice': 'edited notice'}, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.json()['notice'], 'edited notice') 
    
    def test_delete_notice_fails_for_unauthenticated_user(self):
        response = self.client.delete(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 401)
    
    def test_delete_notice_fails_for_non_owner_user(self):
        response = self.client.delete(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 403)
    
    def test_delete_notice_fails_for_nonexistent_notice(self):
        response = self.client.delete(reverse('api_notice_retrieve_update', args=[self.notice.pk + 1]), headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 404)
    
    def test_delete_notice_succeeds_for_owner(self):
        response = self.client.delete(self.get_update_delete_urls, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.get_update_delete_urls)
        self.assertEqual(response.status_code, 404)
    
    def test_list_building_notices_fails_for_unauthenticated_user(self):
        response = self.client.get(self.list_building_notices_url)
        self.assertEqual(response.status_code, 401)

    def test_list_building_notices_fails_for_user_not_linked_to_building(self):
        response = self.client.get(self.list_building_notices_url, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'user profile not linked to building')

    def test_list_building_notices_succeeds_for_tenant(self):
        notices = self.create_building_notices()
        response = self.client.get(self.list_building_notices_url, headers={'Authorization': f'Bearer {self.tenant_token}'})
        self.assertEqual(response.status_code, 200)
        all_notices_ids = list(map(lambda x: x['pk'], response.json()['results']))
        self.assertEqual(len(all_notices_ids), 3)
        self.assertTrue(notices[0].pk in all_notices_ids and notices[1].pk in all_notices_ids and self.notice.pk in all_notices_ids)

    def test_list_building_notices_succeeds_for_owner(self):
        notices = self.create_building_notices()
        response = self.client.get(self.list_building_notices_url, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        all_notices_ids = list(map(lambda x: x['pk'], response.json()['results']))
        self.assertEqual(len(all_notices_ids), 3)
        self.assertTrue(notices[0].pk in all_notices_ids and notices[1].pk in all_notices_ids and self.notice.pk in all_notices_ids)

    def test_list_building_notices_succeeds_for_admin(self):
        notices = self.create_building_notices()
        response = self.client.get(self.list_building_notices_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        all_notices_ids = list(map(lambda x: x['pk'], response.json()['results']))
        self.assertEqual(len(all_notices_ids), 3)
        self.assertTrue(notices[0].pk in all_notices_ids and notices[1].pk in all_notices_ids and self.notice.pk in all_notices_ids)
    
    def test_list_building_notices_fails_for_nonexistent_building(self):
        response = self.client.get(reverse('api_notice_list_by_building', args=[self.building_id + 1]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'Building does not exist')

    def test_list_user_notices_fails_for_unauthenticated_user(self):
        response = self.client.get(self.list_user_notices_url)
        self.assertEqual(response.status_code, 401)

    def test_list_user_notices_fails_for_other_user_access(self):
        response = self.client.get(self.list_user_notices_url, headers={'Authorization': f'Bearer {self.regular_user_token}'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'permission denied')

    def test_list_user_notices_succeeds_for_admin(self):
        notices = self.create_building_notices()
        response = self.client.get(self.list_user_notices_url, headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        all_notices_ids = list(map(lambda x: x['pk'], response.json()['results']))
        self.assertEqual(len(all_notices_ids), 3)
        self.assertTrue(self.notice.pk in all_notices_ids and notices[0].pk in all_notices_ids and notices[1].pk in all_notices_ids)
        response = self.client.get(reverse('api_notice_list_by_user', args=[self.admin.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.json()['results'], [])
    
    def test_list_user_notices_succeeds_for_owner(self):
        notices = self.create_building_notices()
        response = self.client.get(self.list_user_notices_url, headers={'Authorization': f'Bearer {self.owner_token}'})
        self.assertEqual(response.status_code, 200)
        all_notices_ids = list(map(lambda x: x['pk'], response.json()['results']))
        self.assertEqual(len(all_notices_ids), 3)
        self.assertTrue(self.notice.pk in all_notices_ids and notices[0].pk in all_notices_ids and notices[1].pk in all_notices_ids)

    def test_list_user_notices_fails_for_nonexistent_user(self):
        response = self.client.get(reverse('api_notice_list_by_user', args=[self.tenant.pk + self.admin.pk + self.regular_user.pk]), headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'user does not exist')