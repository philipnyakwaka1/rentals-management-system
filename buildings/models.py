from django.db import models
from django.contrib.gis.db import models as gis_models

class Building(models.Model):
    """class to store building shapefiles and associated attributes"""
    
    comment = models.CharField(max_length=255, null=True)
    county = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    rent = models.DecimalField(max_digits=8, decimal_places=2)
    payment_details = models.CharField(max_length=255)
    occupancy = models.BooleanField()
    building_xy = gis_models.PointField(spatial_index=True, srid=21037)

    class Meta:
        db_table = 'building'