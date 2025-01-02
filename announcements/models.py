from django.db import models
from django.contrib.auth.models import User
from buildings.models import Building

class Notice(models.Model):
    """class defining notice table"""
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='notices')
    building = models.ForeignKey(Building, on_delete=models.PROTECT, related_name='notices')
    notice = models.CharField(max_length=256, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.owner.username} Notice'

    class Meta:
        db_table = 'notice'


class Comment(models.Model):
    """class defining comment table"""
    tenant = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='comments', null=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='comments')
    comment = models.CharField(max_length=256, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tenant.username} Announcement'

    class Meta:
        db_table = 'comment'