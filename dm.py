import datetime 
import tweepy
import oauth2 as oauth
import json
import os
from dateutil import parser

CONSUMER_KEY = 	os.getenv('TWITTER_CONSUMER_KEY', None)
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET', None)
ACCESS_KEY = os.getenv('TWITTER_ACCESS_TOKEN_KEY')
ACCESS_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

def parse_tweet():
  consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
  access_token = oauth.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
  client = oauth.Client(consumer, access_token)
  timeline_endpoint = "https://api.twitter.com/1.1/direct_messages.json"
  response, data = client.request(timeline_endpoint)
  tweets = json.loads(data)
  tweet = tweets[0]

  sender_ids= []
  sender_locations = []
  times = []
  texts = []
  harrassment_types = []
  getmetosafety = []
  safe_for_all = []

  for tweet in tweets:
    sender_ids = tweet['sender'] ['id']
    sender_locations = tweet['sender'] ['location']
    times = tweet['created_at']
    texts = tweet['text']
    text_to_parse = str(tweet['text']).lower()
    if text_to_parse.find("No", 0, 5)  != -1:
    	safe_for_all = "No"
    else:
       safe_for_all = "Yes"

    if text_to_parse.find("workplace") != -1:
    	harrassment_types = "workplace"
    elif text_to_parse.find("eveteasing")  != -1:
    	 harrassment_types = "eveteasing"
    elif text_to_parse.find("abuse")  != -1:
    	 harrassment_types = "abuse"
    elif text_to_parse.find("harrassment")  != -1:
    	 harrassment_types = "harrassment"
    else:
         harrassment_types = ('')

    if text_to_parse.find("getmetosafety")  != -1:
      getmetosafety = True
    else: 
      getmetosafety = False 

    
    #Sat Jul 11 22:13:47 +0000 2015
    #time = parser.parse(times).strmp
    time = datetime.datetime.strptime(times, '%a %b %d %H:%M:%S +0000 %Y')


    # direct_message = DM_detail(user_id=sender_ids,location=sender_locations,date=time,category=harrassment_types,raw_text=texts,
    # 	to_safety=getmetosafety)
    # db.session.add(direct_message)
    # db.session.commit()
    print (sender_ids, sender_locations, time, getmetosafety, harrassment_types, texts)


 # incident_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	# user_id = db.Column(db.Integer, nullable=False)
	# location = db.Column(db.String(60), nullable=False)
	# x_cord = db.Column(db.Numeric, nullable=True)
	# y_cord = db.Column(db.Numeric, nullable=True)
	# day_of_week = db.Column(db.String(10), nullable=True)
	# date = db.Column(db.Date, nullable=False)
	# month = db.Column(db.String(10), nullable=True)
	# time = db.Column(db.Time, nullable=False)
	# hour = db.Column(db.String(10), nullable=True)
	# category = db.Column(db.String(60), nullable=True)
	# raw_text = db.Column(db.String(140), nullable=False)
	# data_source = db.Column(db.String(60), nullable=True)
	# to_safety = db.Column(db.String(60), nullable=False)




if __name__ == "__main__":
  parse_tweet()

