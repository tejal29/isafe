import tweepy
import os
from flask import session, request

consumer_key=os.environ['TWITTER_CONSUMER_KEY']
consumer_secret=os.environ['TWITTER_CONSUMER_SECRET']
access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY']
access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']


def twitter_auth():

	print consumer_key

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret,"https://twitter.com")

	# Redirect user to Twitter to authorize
	try:
		redirect_url = auth.get_authorization_url()
	except tweepy.TweepError:
	    print 'Error! Failed to get request token.'


	print auth.request_token

	session.set('request_token', auth.request_token)

	# # Example using callback (web app)
	# verifier = request.GET.get('oauth_verifier')

	# # Let's say this is a web app, so we need to re-build the auth handler
	# # first...
	# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	# token = session.get('request_token')
	# session.delete('request_token')
	# auth.request_token = token

	# try:
	#     auth.get_access_token(verifier)
	# except tweepy.TweepError:
	#     print 'Error! Failed to get access token.'

	# token = auth.access_token
	# secret = auth.access_token_secret

	# print token
	# print secret

	# # Construct the API instance
	# api = tweepy.API(auth)

if __name__ == "__main__":
    twitter_auth()