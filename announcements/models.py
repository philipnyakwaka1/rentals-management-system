from django.db import models
from users.models import Owner, Tenant
from buildings.models import Building

class Notice(models.Model):
    """class defining notice table"""
    owner = models.ForeignKey(Owner, related_name='notices')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='notices')
    notice = models.CharField(max_length=256, null=False)


class Comment(models.Model):
    """class defining comment table"""
    tenant = models.ForeignKey(Tenant, related_name='comments')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='comments')
    comment = models.CharField(max_length=256, null=False)
