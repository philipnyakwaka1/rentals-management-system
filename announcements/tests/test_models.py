from django.test import TestCase
from django.contrib.auth.models import User
from announcements.models import Notice, Comment
from buildings.models import Building
from django.contrib.gis.geos import Point
from django.db.models.deletion import ProtectedError


class NoticeTestCase(TestCase):

    def setUp(self):
        self.owner = User.objects.create(username='owner', password='owner@123')
        self.building = Building.objects.create(building=Point(34.0, -4.0))
        self.owner_notice = Notice.objects.create(owner=self.owner, building=self.building, notice='rent is overdue')
    
    def test_prevent_delete_user_with_notice(self):
        user = User.objects.get(username='owner')
        with self.assertRaises(ProtectedError):
            user.delete()
    
    def test_prevent_delete_building_with_notice(self):
        building = Building.objects.get(pk=self.building.pk)
        with self.assertRaises(ProtectedError):
            building.delete()

    def test_delete_notice(self):
        notice = Notice.objects.get(pk=self.owner_notice.pk)
        self.assertEqual(notice.owner, self.owner)
        self.assertEqual(notice.building, self.building)
        notice.delete()
        owner = User.objects.get(username='owner')
        building = Building.objects.get(pk=self.building.pk)
        self.assertFalse(owner.notices.all().exists())
        self.assertFalse(building.notices.all().exists())
    
    def test_update_notice(self):
        notice = Notice.objects.get(pk=self.owner_notice.pk)
        notice.notice = 'payment deadline has been extended by one week'
        notice.save()
        self.assertTrue(self.owner_notice.created_at == notice.created_at)
        self.assertTrue(notice.updated_at > self.owner_notice.updated_at)
        self.assertTrue(notice.notice != self.owner_notice.notice)
        

class CommentTestCase(TestCase):
     
    def setUp(self):
        self.tenant = User.objects.create(username='tenant', password='tenant@123')
        self.building = Building.objects.create(building=Point(34.0, -4.0))
        self.tenant_comment = Comment.objects.create(tenant=self.tenant, building=self.building, comment='Leaking roofs')

    def test_delete_comment_upon_delete_building(self):
        building = Building.objects.get(pk=self.building.pk)
        building.delete()
        with self.assertRaises(Comment.DoesNotExist):
            comment = Comment.objects.get(tenant=self.tenant)
    
    def test_comment_value_upon_delete_tenant(self):
        tenant = User.objects.get(username='tenant')
        tenant.delete()
        comment = Comment.objects.get(pk=self.tenant_comment.pk)
        self.assertEqual(comment.tenant, None)


    def test_update_comment(self):
        comment = Comment.objects.get(pk=self.tenant_comment.pk)
        comment.comment = 'The roof has been fixed. All good.'
        comment.save()
        self.assertTrue(self.tenant_comment.created_at == comment.created_at)
        self.assertTrue(comment.updated_at > self.tenant_comment.updated_at)
        self.assertTrue(comment.comment != self.tenant_comment.comment)