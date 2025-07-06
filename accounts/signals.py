from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        full_name = str(instance.first_name + " " + instance.last_name)
        UserProfile.objects.create(user=instance, full_name=full_name)

    else:
        instance.profile.save()