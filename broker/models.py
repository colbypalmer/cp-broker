from django.db import models
from django.contrib.auth.models import User
from django.dispatch.dispatcher import receiver
from django_facebook.models import FacebookModel
from django.db.models.signals import post_save
from django_facebook.utils import get_user_model, get_profile_model


class Service(models.Model):
    name = models.CharField(max_length=75)
    url = models.URLField(blank=True, null=True)


class Connection(models.Model):
    user = models.ForeignKey(User)
    provider = models.CharField(max_length=75)
    uid = models.IntegerField(null=True, blank=True)
    token = models.CharField(max_length=255)
    secret = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True, auto_now=True, editable=False)

    def __unicode__(self):
        if not self.username:
            return '{}: {}'.format(self.provider, self.uid)
        else:
            return '{}: {}'.format(self.provider, self.username)


class FacebookProfile(FacebookModel):
    user = models.OneToOneField(User, related_name='profile')


@receiver(post_save)
def create_profile(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if sender == get_user_model():
        user = instance
        profile_model = get_profile_model()
        if profile_model == FacebookProfile and created:
            profile, new = FacebookProfile.objects.get_or_create(user=instance)