from django.db import models
from django.contrib.gis.db import models as gis_models

class Building(models.Model):
    """class to store building shapefiles and associated attributes"""
    coordinate_str = models.CharField(max_length=50)
    comment = models.CharField(max_length=255, null=True, default=None)
    county = models.CharField(max_length=255, null=True, default=None)
    district = models.CharField(max_length=255, null=True, default=None)
    rent = models.DecimalField(max_digits=8, decimal_places=2, null=True, default=None)
    payment_details = models.CharField(max_length=255, null=True, default=None)
    occupancy = models.BooleanField(default=False)
    building_xy = gis_models.PointField(spatial_index=True, srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #image
    #video

    def __str__(self):
        return self.coordinate_str

    class Meta:
        db_table = 'building'