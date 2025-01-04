from django.db import models
from buildings.models import Building
from django.contrib.auth.models import User

class Profile(models.Model):
    """Define owner table"""
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name='profile', null=True)
    phone = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=100, null=True)
    buildings = models.ManyToManyField(Building, through='UserBuilding',related_name='profile')
    #contract

    def __str__(self):
        return f'{self.user.username} Profile'

    class Meta:
        db_table = 'profile'

class UserBuilding(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=6)