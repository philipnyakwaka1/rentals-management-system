from django.db import models
from django.contrib.gis.db import models as gis_models

class Building(models.Model):
    """class to store building shapefiles and associated attributes"""
    comment = models.CharField(max_length=255, null=True, default=None)
    county = models.CharField(max_length=255, null=True, default=None)
    district = models.CharField(max_length=255, null=True, default=None)
    rent = models.DecimalField(max_digits=8, decimal_places=2, null=True, default=None)
    payment_details = models.CharField(max_length=255, null=True, default=None)
    occupancy = models.BooleanField(default=False)
    building = gis_models.PointField(spatial_index=True, srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #image
    #video

    def __str__(self):
        owners = self.profile.all()
        return f'[{self.building.x}, {self.building.y}] - (owners: {", ".join(x.user.username for x in owners)})'

    class Meta:
        db_table = 'building'