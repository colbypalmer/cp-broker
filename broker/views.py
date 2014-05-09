import tweepy

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views.generic import View, DetailView
from models import Service, Connection, FacebookProfile


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

            # Check to make sure we have a FacebookProfile
            fb_profile = FacebookProfile.objects.get_or_create(user=request.user)
            return render(request, 'broker/facebook_connect.html', {'fb_profile': fb_profile})
