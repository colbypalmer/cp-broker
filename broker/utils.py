from django.conf import settings
import tweepy


def twitter_client(connection):
    auth = tweepy.OAuthHandler(settings.TWITTER_APP_API_KEY, settings.TWITTER_APP_API_SECRET)
    auth.set_access_token(connection.token, connection.secret)
    return tweepy.API(auth)