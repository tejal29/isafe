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
from dm import parse_tweets
from engine.initiate_dm import get_ngo, initiate_dm

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

TWITTER_REQUEST_TOKEN = 'https://api.twitter.com/oauth/request_token'

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

DATABASE_URL = os.environ.get("DATABASE_URL",
                              "postgresql://localhost/isafe_db")

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
   
    return render_template("HomePage.html")

@app.route('/heat')
def show_heat():
    """Show heatmap"""

    return render_template("heatmap.html")

@app.route('/reported_incidents')
def show_reported_incidents():
    """Shows partners on map."""
   
    return render_template("markers.html")

@app.route('/counselling')
def show_table():
  connections = Connection.query.all()
  volunteers = NGO.query.all()
  items = []
  for connection in connections:
   item = {}
   item['type'] = connection.category 
   item['status'] = connection.status_code
   for volunteer in volunteers:
     if volunteer.twitter_user_id == connection.NGO_id:
       item['name'] = volunteer.name
   items.append(item)
  return render_template("counsel.html", items=items)

@app.route('/volunteers')
def show_partners_map():
    """Shows partners on map."""
    volunteers = NGO.query.all() 
    return render_template("volunteers.html", volunteers=volunteers)

@app.route('/partner_form')
def show_organization_form():
    """Shows form for organizations/NGOs to complete."""

   
    return render_template("partner_form.html")

@app.route('/get_partners')
def show_partners():
    """Get JSON objects for partners."""

    return NGO.get_features_objects()

@app.route('/get_markers')
def get_marker_points():
    """Get JSON objects for marker points."""

    start_date = request.args.get("start_date") #start_date and end_date are defined in the event listener in javascript and passed into Flask
    end_date = request.args.get("end_date")

    if start_date:                              #if the user enters in a start_date

        print start_date

        start_date_formatted = datetime.strptime(start_date,"%Y-%m-%d") #reformat start and end dates as date objects
        end_date_formatted = datetime.strptime(end_date,"%Y-%m-%d")
        
        return DM_detail.get_features_objects_by_date(start_date_formatted,end_date_formatted) #call class method that will return GeoJSON features


    else:                               # user has not entered in a date, use a default period
        
        end_date = datetime.now()                    
        start_date = end_date - timedelta(days=15)

        print start_date

        return DM_detail.get_features_objects_by_date(start_date,end_date)

@app.route('/petition')
def petition():
    """Create Petition"""
    # No api for quering petition
    petitions = []
    petitions.append({'title': 'Increase Patrol in Sector 5 Delhi after 6 p.m', 
                       'signature_count': '5331', 
                       'goal': '10000', 
                       'url': ''})
    cities = ['Indira Nagar, Delhi', 'Sector 10, Kolkotta']
    #cities = DangerCities.query.group_by(DM_detail.location).count
    return render_template("petition_form.html", petitions=petitions, cities=cities)

@app.route('/get_heat')
def get_heat_points():
    """Make JSON objects for markers on heatmap."""

    start_date = request.args.get("start_date") #start_date and end_date are defined in the event listener in javascript and passed into Flask
    end_date = request.args.get("end_date")

    if start_date:                              #if the user enters in a start_date

        print start_date
        print end_date

        start_date_formatted = datetime.strptime(start_date,"%Y-%m-%d") #reformat start and end dates as date objects
        end_date_formatted = datetime.strptime(end_date,"%Y-%m-%d")
        
        return DM_detail.get_features_objects_by_date(start_date_formatted,end_date_formatted)

    else:                               # user has not entered in a date, use a default period
        
        end_date = datetime.now()                    
        start_date = end_date - timedelta(days=15)

        print start_date

        return DM_detail.get_features_objects_by_date(start_date,end_date)

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
    session['user_id'] = g.twitter_info['user_id']
    session['oauth_token'] = g.twitter_info['oauth_token']
    session['oauth_token_secret'] = g.twitter_info['oauth_token_secret']
    user_id  = session['user_id']
    user_token = session['oauth_token']
    user_secret = session['oauth_token_secret']
    org_name = session["org_name"]
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
        organization = NGO(org_name=org_name,name=name,email=email, twitter_handle=twitter_handle,address=address,description=description,category=category,
        x_cord=x_cord,y_cord=y_cord,phone=phone,twitter_user_id=user_id,twitter_user_token=user_token,twitter_user_secret=user_secret)
        
        db.session.add(organization)

    db.session.commit() 

    return redirect('/')

@app.route('/twitter_signin', methods=["GET","POST"])
def twitter_auth():
    """Twitter authorization."""

    org_name = request.args.get("org_name")
    name = request.args.get("name")
    email = request.args.get("email")
    phone = request.args.get("phone")
    twitter_handle = request.args.get("twitter")
    address = request.args.get("address")
    description = request.args.get("description")

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
    session["org_name"] = org_name
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

@app.route('/fetch/')
def fetch_dms():
 fetch_stats =[]
 processed_incidents = parse_tweets()
 print processed_incidents
 for incident in processed_incidents:
   #ngo = NGO.query.filter_by(address=location).first()
   ngo = get_ngo(incident['location'])
   print(ngo)
   fetch_stats.append('Contacted Volunteer %s  @%s from %s' %(ngo.name, ngo.twitter_handle, ngo.address))
   initiate_dm(ngo.twitter_handle, incident['victim_id'], ngo.twitter_user_token, ngo.twitter_user_secret)
   fetch_stats.append('Volunteer @%s now follows Inceident Reporter %s' %(ngo.twitter_handle, incident['victim_id']))
   fetch_stats.append('Send sms to Incident Reporter to follow @%s' %ngo.twitter_handle)
   fetch_stats.append('Send an SMS on behalf of NGO representative to Incident Reporter')
   if Connection.query.filter_by(user_id=incident['victim_id'], NGO_id=ngo.twitter_user_id).count <1:
     connections = Connection(user_id=incident['victim_id'], NGO_id=ngo.twitter_user_id, category='harrasment',description='Just started a counselling', status_code='In Progress')
     db.session.add(connections)
     db.session.commit()
 print(fetch_stats)
 return render_template("fetch_stats.html", fetch_stats=fetch_stats)

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
