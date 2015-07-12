import tweepy
import oauth2 as oauth
import json

CONSUMER_KEY = 	"RxpTHwI45jg00nVDYzDssLVMr"
CONSUMER_SECRET = "DLr5DASKgqLwulhDyViBHcSLa1Hqx5ML5NT3o1kHsKwKmB6E6d"
ACCESS_KEY = "3273730339-vnnuN4pmjeUyXSWVGH3T3uVclMGfXfy7f1RcEWS"
ACCESS_SECRET = "w5XVprLj5Y0kKzugX18BGGYlo90QD0Ym6wH9G7VySgiis"
tweets = []
safe_for_all = []
workplace = []
eveteasing = []
abuse = []
harrassment = []
getmetosafety = []

def parse_tweet():
  consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
  access_token = oauth.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
  client = oauth.Client(consumer, access_token)
  timeline_endpoint = "https://api.twitter.com/1.1/direct_messages.json"
  response, data = client.request(timeline_endpoint)
  tweets = json.loads(data)
  tweet = tweets[0]

  sender_ids = []
  sender_locations = []
  times = []
  texts = []
  harrassment_types = []
  getmetosafety = []
  safe_for_all = []

  for tweet in tweets:
    sender_ids.append(tweet['sender'] ['id']) 
    sender_locations.append(tweet['sender'] ['location'])
    times.append(tweet['created_at'])
    texts.append(tweet['text'])
    text_to_parse = str(tweet['text']).lower()
    if text_to_parse.find("No", 0, 5)  != -1:
    	safe_for_all.append("No")
    else:
       safe_for_all.append("Yes")

    if text_to_parse.find("workplace") != -1:
    	harrassment_types.append("workplace")
    elif text_to_parse.find("eveteasing")  != -1:
    	 harrassment_types.append("eveteasing")
    elif text_to_parse.find("abuse")  != -1:
    	 harrassment_types.append("abuse")
    elif text_to_parse.find("harrassment")  != -1:
    	 harrassment_types.append("harrassment")
    else:
         harrassment_types.append('')

    if text_to_parse.find("getmetosafety")  != -1:
      getmetosafety.append(True)
    else: 
      getmetosafety.append(False) 
  print (sender_ids, sender_locations, times, getmetosafety, harrassment_types, texts)




if __name__ == "__main__":
  parse_tweet()

