from django.test import TestCase
from buildings.models import Building
from users.models import Profile, UserBuilding
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point

class UserBuildingTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(username='test_user1', password='test_user1@123')
        self.user2 = User.objects.create(username='test_user2', password='test_user2@123')
        self.building1 = Building.objects.create(building=Point(34.5, -4.0))
        user1_profile = Profile.objects.get(user=self.user1)
        user1_profile.buildings.add(self.building1, through_defaults={'relationship': 'Owner'})
        user2_profile = Profile.objects.get(user=self.user2)
        user2_profile.buildings.add(self.building1, through_defaults={'relationship': 'Owner'})
    
    def test_building_geometry(self):
        self.assertEqual(self.building1.building.x, 34.5)
        self.assertEqual(self.building1.building.y, -4.0)
        self.assertEqual(self.building1.building.srid, 4326)
        self.assertEqual(type(self.building1.building), Point)
    
    def test_profile_linked_to_building(self):
        profile = Profile.objects.get(user=self.user1)
        profile_building = profile.buildings.all().first()
        self.assertEqual(profile_building.profile.all().first(), profile)
    
    def test_building_linked_to_profiles(self):
        user1_profile = Profile.objects.get(user=self.user1)
        building_profiles = user1_profile.buildings.all().first().profile.all()
        self.assertTrue(self.user1.profile in building_profiles)
        self.assertTrue(self.user2.profile in building_profiles)
    
    def test_delete_building_if_no_linked_profile(self):
        user1_profile = Profile.objects.get(user=self.user1)
        user1_profile.delete()
        user2_profile = Profile.objects.get(user=self.user2)
        building_profiles = user2_profile.buildings.all().first().profile.all()
        self.assertEqual(len(building_profiles), 1)
        self.assertEqual(building_profiles.first(), self.user2.profile)
        self.assertTrue(self.user1.profile not in building_profiles)
        building_id = self.user2.profile.buildings.all().first().id
        building_cache = Building.objects.get(pk=building_id)
        user2_profile.delete()

        with self.assertRaises(Building.DoesNotExist):
            building = Building.objects.get(pk=building_id)
            
        with self.assertRaises(UserBuilding.DoesNotExist):
            building = UserBuilding.objects.get(building=building_cache)
        
        