import datetime
import json
import tweepy
import urllib
import urlparse
from dateutil import parser

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic import View, DetailView

from .models import Service, Connection, FacebookProfile


class BrokerListView(View):

    def get(self, request):

        services = Service.objects.all()

        if request.user.is_staff:
            connections = Connection.objects.all()
        else:
            connections = Connection.objects.filter(user=request.user)
        context = dict(services=services, connections=connections)
        return render(request, 'broker/list.html', context)

    def post(self, request):
        raise Http404


class BrokerDetailView(DetailView):

    model = Connection
    template_name = 'broker/detail.html'


class BrokerServiceNewView(DetailView):

    model = Connection

    def get(self, request, *args, **kwargs):

        if self.kwargs['slug'] == 'twitter':

            if ('oauth_token' and 'oauth_verifier') in request.GET:

                verifier = request.GET['oauth_verifier']
                auth = tweepy.OAuthHandler(settings.TWITTER_APP_API_KEY, settings.TWITTER_APP_API_SECRET)
                token = request.session.get('request_token')
                try:
                    del request.session['request_token']
                except KeyError:
                    pass
                auth.set_request_token(token[0], token[1])
                try:
                    auth.get_access_token(verifier)
                except tweepy.TweepError:
                    print 'Error! Failed to get access token.'

                oauth_key = auth.access_token.key
                secret = auth.access_token.secret
                auth.set_access_token(oauth_key, secret)
                api = tweepy.API(auth)

                profile = api.verify_credentials()
                username = profile.screen_name
                user_id = profile.id

                connection, created = Connection.objects.get_or_create(username=username,
                                                                       provider='twitter', user=request.user)
                connection.token = oauth_key
                connection.secret = secret
                connection.uid = user_id
                connection.save()

                return HttpResponseRedirect(reverse('broker_list'))

            auth = tweepy.OAuthHandler(settings.TWITTER_APP_API_KEY, settings.TWITTER_APP_API_SECRET)
            try:
                redirect_url = auth.get_authorization_url()
            except tweepy.TweepError:
                raise ValueError('Error! Failed to get request token.')

            request.session['request_token'] = (auth.request_token.key, auth.request_token.secret)
            return HttpResponseRedirect(redirect_url)

        elif self.kwargs['slug'] == 'facebook':

            scope = 'public_profile,user_photos,user_status,user_videos'

            args = dict(client_id=settings.FACEBOOK_APP_ID, scope=scope,
                        redirect_uri=u'http://{}{}'.format(request.META['HTTP_HOST'], request.META['PATH_INFO']))

            if 'code' in request.GET:  # process FB auth token

                args['client_secret'] = settings.FACEBOOK_APP_SECRET
                args['code'] = request.GET['code']
                response = urlparse.parse_qs(urllib.urlopen(
                    'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(args)).read())
                access_token = response['access_token'][-1]
                expiry = int(response['expires'][-1])
                now = datetime.datetime.now()
                expires_at = now + datetime.timedelta(seconds=expiry)

                # Get user profile
                profile_json = json.load(urllib.urlopen(
                    'https://graph.facebook.com/me?' + urllib.urlencode(dict(access_token=access_token))))

                connection, created = Connection.objects.get_or_create(user=request.user, provider='facebook')
                connection.uid = profile_json['id']
                connection.token = access_token
                connection.token_expires = expires_at
                connection.save()
                profile, created = FacebookProfile.objects.get_or_create(connection=connection)
                profile.about = profile_json['about']
                profile.bio = profile_json['bio']
                profile.name = profile_json['name']
                profile.profile_url = profile_json['link']
                profile.website_url = profile_json['website']
                profile.date_of_birth = parser.parse(profile_json['birthday']).strftime('%Y-%m-%d')
                profile.gender = profile_json['gender']
                profile.raw_data = profile_json
                profile.save()

                return HttpResponseRedirect(reverse('broker_list'))

            else:

                try:
                    fb_connection = Connection.objects.get(provider='facebook', user=request.user)
                except ObjectDoesNotExist:
                    return HttpResponseRedirect('https://graph.facebook.com/oauth/authorize?' + urllib.urlencode(args))

                return render(request, 'broker/facebook_connect.html', {'fb_connection': fb_connection})
