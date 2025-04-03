from django.test import TestCase
from users.models import UserBuilding, Profile
from django.contrib.auth.models import User
from buildings.models import Building


class UserProfileTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user', password='test_user@123')
    
    def test_profile_creation(self):
        profile = Profile.objects.get(user=self.user)
        self.assertTrue(profile)
    
    def test_user_deletion(self):
        user = User.objects.get(username='test_user')
        user.delete()
        with self.assertRaises(Profile.DoesNotExist):
            profile = Profile.objects.get(user=self.user)
    
    def test_profile_deletion(self):
        profile = Profile.objects.get(user=self.user)
        profile.delete()
        user = User.objects.get(username='test_user')
        with self.assertRaises(Profile.DoesNotExist):
            user.profile
    
    def test_dunder_string(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(str(profile), 'test_user Profile')
    
    def test_update_profile(self):
        profile = Profile.objects.get(user=self.user)
        profile.phone = '+905345982367'
        profile.address = 'Yedikule, Fatih'
        profile.save()
        user = User.objects.get(username='test_user')
        self.assertEqual(user.profile.phone, '+905345982367')
        self.assertEqual(user.profile.address, 'Yedikule, Fatih')

class UserBuildingTestCase(TestCase):
    #test many-to-many relationships, ensure a building can be associated to user through profile
    #test deletion
    #Test relationship field constraints: Ensure the relationship field properly stores values (e.g., enforce max_length=6).
    pass