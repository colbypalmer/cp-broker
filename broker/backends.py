import json
from django_facebook import settings as facebook_settings
from django_facebook.registration_backends import FacebookRegistrationBackend
from django_facebook.connect import CONNECT_ACTIONS
from django_facebook.utils import next_redirect
from functools import partial
from models import FacebookProfile
from broker.models import Connection


class BrokerFacebookRegistrationBackend(FacebookRegistrationBackend):
    def post_connect(self, request, user, action):
        # go as crazy as you want, just be sure to return a response
        fb = FacebookProfile.objects.get(user=user)
        connection, created = Connection.objects.get_or_create(provider='facebook', user=user)
        connection.uid = fb.facebook_id
        connection.token = fb.access_token
        connection.username = json.loads(fb.raw_data)['username']
        connection.save()

        default_url = facebook_settings.FACEBOOK_LOGIN_DEFAULT_REDIRECT
        base_next_redirect = partial(
            next_redirect, request, default=default_url)

        if action is CONNECT_ACTIONS.LOGIN:
            response = base_next_redirect(next_key=['login_next', 'next'])
        elif action is CONNECT_ACTIONS.CONNECT:
            response = base_next_redirect(next_key=['connect_next', 'next'])
        elif action is CONNECT_ACTIONS.REGISTER:
            response = base_next_redirect(next_key=['register_next', 'next'])
        else:
            raise ValueError

        return response
