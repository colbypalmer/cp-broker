from django.db import models
from django.contrib.auth.models import User

class Service(models.Model):
    name = models.CharField(max_length=75)
    url = models.URLField(blank=True, null=True)


class Connection(models.Model):
    user = models.ForeignKey(User)
    provider = models.CharField(max_length=75)
    uid = models.BigIntegerField(null=True, blank=True)
    token = models.CharField(max_length=255)
    token_expires = models.DateTimeField(null=True, blank=True)
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


class FacebookProfile(models.Model):
    connection = models.ForeignKey(Connection, related_name='connection_facebook', null=True, blank=True)
    about = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    profile_url = models.TextField(blank=True, null=True)
    website_url = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=6, choices=(('male', 'Male'), ('female', 'Female')), blank=True, null=True)
    raw_data = models.TextField(blank=True, null=True)
    new_token_required = models.BooleanField(default=False,
                                             help_text='Set to true if the access token is outdated, '
                                                       'or if it lacks permissions')
