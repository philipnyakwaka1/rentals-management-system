from django.db import models
from buildings.models import Building
from django.contrib.auth.models import User

class Profile(models.Model):
    """Define owner table"""
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name='owner', null=True)
    building_coordinate = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=20, name=False)
    address = models.CharField(max_length=100, null=False)
    building = models.ManyToManyField(Building, related_name='owners')
    #user_type
    #contract

    class Meta:
        db_table = 'profile'

