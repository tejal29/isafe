import os
import logging
import tweepy
from model import NGO 

ConsumerKey = os.getenv('TWITTER_CONSUMER_KEY', None)
ConsumerSecret = os.getenv('TWITTER_CONSUMER_SECRET', None)
AccessKey = os.getenv('TWITTER_ACCESS_TOKEN_KEY')
AccessSecret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

Tejal = '78686298'
Shabnam = '281702049'

logging.basicConfig()
logger = logging.getLogger("engine")

def initiate_dm(ngo_rep, victim_id, key, secret):
  try:
    logger = logging.getLogger("engine")
    auth = tweepy.OAuthHandler(ConsumerKey, ConsumerSecret)
    auth.set_access_token(AccessKey, AccessSecret)
    api = tweepy.API(auth)
    text = 'D {0} Follow {1}. He/She is your system assigned representative.'.format(victim_id, ngo_rep)
    api.send_direct_message(user_id=victim_id, text=text)
    logger.info('Sent {0} to {1}'.format(text, victim_id))
  except Exception:
    print("Could not follow")
  try:
    # Todo Fetch the tokens for ngo from database
    text = "Hello Friend! I am your ISafe help. Tell me more about."
    auth.set_access_token(key, secret)
    api = tweepy.API(auth)
    api.create_friendship(victim_id)
    api.send_direct_message(user_id=victim_id, text=text)
  except Exception:
    print("Could not send")

def get_ngo(location):
  ngo = NGO.query.filter_by(address=location).first()
  return ngo
  
if __name__ == "__main__":
  initiate_dm(Shabnam, Tejal, '', '')
