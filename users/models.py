from django.db import models
from buildings.models import Building

class Owner(models.Model):
    """Define owner table"""
    username = models.CharField(max_length=50, null=False)
    building_coordinate = models.CharField(max_length=50, null=False)
    f_name = models.CharField(max_length=50, null=False)
    l_name = models.CharField(max_length=50, null=False)
    phone = models.CharField(max_length=20, name=False)
    email = models.CharField(max_length=50, null=False)
    address = models.CharField(max_length=100, null=False)
    buiilding = models.ManyToManyField(Building, related_name='owners')

    class Meta:
        db_table = 'owner'

class Tenant(models.Model):
    """Define tenant table"""
    username = models.CharField(max_length=50, null=False)
    f_name = models.CharField(max_length=50, null=False)
    l_name = models.CharField(max_length=50, null=False)
    phone = models.CharField(max_length=20, name=False)
    email = models.CharField(max_length=50, null=False)
    address = models.CharField(max_length=100, null=False)
    building = models.ManyToManyField(Building, related_name='tenants')
    #contract(File)
    
    class Meta:
        db_table = 'tenant'