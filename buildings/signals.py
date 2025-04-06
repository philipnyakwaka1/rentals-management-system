from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from users.models import Profile


@receiver(pre_delete, sender=Profile)
def save_related_buildings_before_profile_delete(sender, instance, **kwargs):
    instance._related_buildings = list(instance.buildings.all())

@receiver(post_delete, sender=Profile)
def delete_orphaned_buildings_after_profile_delete(sender, instance, **kwargs):
    for building in instance._related_buildings:
        if not building.profile.all().exists():
            building.delete()
