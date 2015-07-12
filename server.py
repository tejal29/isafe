from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
from model import DM_detail, NGO, Connection, Category, Status, connect_to_db, db
import json
import requests
from sqlalchemy import desc
import csv
from datetime import datetime, timedelta
import time
import ast
import os
import tweepy
from flask_oauth import OAuth

consumer_key=os.environ['TWITTER_CONSUMER_KEY']
consumer_secret=os.environ['TWITTER_CONSUMER_SECRET']
access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY']
access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']

oauth = OAuth()

twitter = oauth.remote_app('twitter',
  base_url='https://api.twitter.com/1.1/',
  request_token_url='https://api.twitter.com/oauth/request_token',
  access_token_url='https://api.twitter.com/oauth/access_token',
  authorize_url='https://api.twitter.com/oauth/authenticate',
  consumer_key=consumer_key,
  consumer_secret=consumer_secret
)

print "this is runnign"

print twitter

TWITTER_REQUEST_TOKEN = 'https://api.twitter.com/oauth/request_token'

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

DATABASE_URL = os.environ.get("DATABASE_URL",
                              "postgresql://localhost/isafe-db")

secret_key = os.environ.get("FLASK_SECRET_KEY", "ABC")

app.config['secret_key'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

app.jinja_env.undefined = StrictUndefined


# ========================================================================
# Before zone

@app.before_request
def before_request():
  """Function called on each request.
  """
  print session.get('user_id', None)


@app.route('/')
def index():
    """Homepage."""
   
    return render_template("base.html")

@app.route('/organizations')
def show_organization_form():
    """Shows form for organizations/NGOs to complete."""

    print twitter
   
    return render_template("organization_form.html")

@app.route('/save_org_info')
def process_report():
    """Save reported crime to database."""

    name = request.args.get("name")
    email = request.args.get("email")
    phone = request.args.get("phone")
    twitter = request.args.get("twitter")
    address = request.args.get("address")
    description = request.args.get("description")

    print name
    print email

    categories = str(request.args.get("categories")) #put JS returned into string
    categories_list = categories.strip("]").strip("[").split(",") #put string into list
    category_list = []

    for category in categories_list:    #iterate through the list to strip out quotes and add to a list
        category_stripped = category.strip('"')
        category_list.append(category_stripped)

    #use the Mapbox geocoder API to get the coordinates of the addressed inputted
    geocode = requests.get("http://api.tiles.mapbox.com/v4/geocode/mapbox.places/'%s'.json?access_token=pk.eyJ1Ijoic2hhYmVtZGFkaSIsImEiOiIwckNSMkpvIn0.MeYrWfZexYn1AwdiasXbsg" % address)
    geocode_text = geocode.text     #put the response into text
    geocode_json = json.loads(geocode_text) #read in as json

    coordinates = geocode_json["features"][0]["geometry"]["coordinates"]    #this will return the coordinates of the first returned location, sometimes there is more than one, maybe deal with this later

    y_cord = coordinates[0]
    x_cord = coordinates[1]

    organization = NGO(org_name=name,email=email, twitter_handle=twitter,address=address,description=description,category=category,
        x_cord=x_cord,y_cord=y_cord,phone=phone)

    db.session.add(incident)

    db.session.commit()    

    return redirect('/organizations')

@twitter.tokengetter
def get_twitter_token():
  """
  This is used by the API to look for the auth token and secret
  it should use for API calls.  During the authorization handshake
  a temporary set of token and secret is used, but afterwards this
  function has to return the token and secret.  If you don't want
  to store this in the database, consider putting it into the
  session instead.
  """
  if hasattr(g, 'twitter_info'):
    return g.twitter_info['oauth_token'], g.twitter_info['oauth_token_secret']
  else:
    g.twitter_info = {}

@app.route('/twitter_auth', methods=["GET"])
@twitter.authorized_handler
def get_oauth_token(resp):

    g.twitter_info = {
        'oauth_token': resp['oauth_token'],
        'oauth_token_secret': resp['oauth_token_secret'],
        'screen_name': resp['screen_name'],
        'user_id': resp['user_id']
    }
    profile = get_twitter_profile(resp['user_id'])
    print ''
    print profile
    print ''
    session['user_id'] = g.twitter_info['user_id']
    session['oauth_token'] = g.twitter_info['oauth_token']
    session['oauth_token_secret'] = g.twitter_info['oauth_token_secret']
    user_id  = session['user_id']
    user_token = session['oauth_token']
    user_secret = session['oauth_token_secret']
    name = session["name"]
    email = session["email"]
    twitter_handle = session["twitter_handle"]
    address = session["address"]
    description = session["description"]
    categories = session["category"]
    x_cord = session["x_cord"]
    y_cord = session["y_cord"]
    phone = session["phone"]

    for category in categories:
        organization = NGO(org_name=name,email=email, twitter_handle=twitter_handle,address=address,description=description,category=category,
        x_cord=x_cord,y_cord=y_cord,phone=phone,twitter_user_id=user_id,twitter_user_token=user_token,twitter_user_secret=user_secret)
        
        db.session.add(organization)

    db.session.commit() 

    return redirect('/')

@app.route('/twitter_signin', methods=["GET","POST"])
def twitter_auth():
    """Twitter authorization."""

    name = request.args.get("name")
    email = request.args.get("email")
    phone = request.args.get("phone")
    twitter_handle = request.args.get("twitter")
    address = request.args.get("address")
    description = request.args.get("description")

    print name
    print email

    categories = str(request.args.get("categories")) #put JS returned into string
    categories_list = categories.strip("]").strip("[").split(",") #put string into list
    category_list = []

    for category in categories_list:    #iterate through the list to strip out quotes and add to a list
        category_stripped = category.strip('"')
        category_list.append(category_stripped)

    #use the Mapbox geocoder API to get the coordinates of the addressed inputted
    geocode = requests.get("http://api.tiles.mapbox.com/v4/geocode/mapbox.places/'%s'.json?access_token=pk.eyJ1Ijoic2hhYmVtZGFkaSIsImEiOiIwckNSMkpvIn0.MeYrWfZexYn1AwdiasXbsg" % address)
    geocode_text = geocode.text     #put the response into text
    geocode_json = json.loads(geocode_text) #read in as json

    coordinates = geocode_json["features"][0]["geometry"]["coordinates"]    #this will return the coordinates of the first returned location, sometimes there is more than one, maybe deal with this later

    y_cord = coordinates[0]
    x_cord = coordinates[1]

    session["name"] = name
    session["email"] = email
    session["phone"] = phone
    session["twitter_handle"] = twitter_handle
    session["address"] = address
    session["description"] = description
    session["category"] = category_list
    session["y_cord"] = y_cord
    session["x_cord"] = x_cord

    return twitter.authorize(callback='/twitter_auth')

def get_twitter_profile(user_id):
  """ """
  resp = twitter.get('users/show.json?user_id={}'.format(user_id))
  if resp.status != 200:
    twitter_profile = None
  if resp.status == 200:
    profile = resp.data
    profile_image_url = profile.get('profile_image_url', '')
    profile_image_url = profile_image_url.replace('_normal', '')
    twitter_profile = {
      "id": profile.get('id_str', ''),
      "name": profile.get('name', ''),
      "profile_image_url": profile_image_url,
      "created_at": profile.get('created_at', ''),
      "location": profile.get('location', ''),
      "lang": profile.get('lang', ''),
      "description": profile.get('description', ''),
      "screen_name": profile.get('screen_name', '')
    }
  return twitter_profile

@app.route('/logout/')
def logout():
  """ """
  session.pop('client_id', None)
  session.pop('client_secret', None)
  session.pop('user_id', None)
  session.pop('oauth_token', None)
  session.pop('oauth_token_secret', None)
  return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    # app.debug = True

    connect_to_db(app)

    DEBUG = "NO_DEBUG" not in os.environ

    PORT = int(os.environ.get("PORT", 5000))

    app.run(debug=DEBUG, host="0.0.0.0", port=PORT)


    # Use the DebugToolbar
    # DebugToolbarExtension(app)
    # app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False #this is so the toolbar does not interrupt redirects

    # app.run()
