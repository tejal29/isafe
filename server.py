from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
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

consumer_key=os.environ['TWITTER_CONSUMER_KEY']
consumer_secret=os.environ['TWITTER_CONSUMER_SECRET']
access_token_key=os.environ['TWITTER_ACCESS_TOKEN_KEY']
access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

DATABASE_URL = os.environ.get("DATABASE_URL",
                              "postgresql://localhost/isafe_db")

secret_key = os.environ.get("FLASK_SECRET_KEY", "ABC")

app.config['secret_key'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Homepage."""
   
    return render_template("homepage.html")

@app.route('/heat')
def show_heat():
    """Show heatmap"""

    return render_template("heatmap.html")

    
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
        
        return Crime_Stat.get_features_objects_by_date(start_date_formatted,end_date_formatted)

    else:                               # user has not entered in a date, use a default period
        
        end_date = datetime.now()                    
        start_date = end_date - timedelta(days=15)

        print start_date

        return Crime_Stat.get_features_objects_by_date(start_date,end_date)

@app.route('/points-of-interest')
def show__markers():
    """Show map with markers."""

    return render_template("markers.html")


@app.route('/get_markers')
def get_marker_points():
    """Get JSON objects for marker points."""

    start_date = request.args.get("start_date") #start_date and end_date are defined in the event listener in javascript and passed into Flask
    end_date = request.args.get("end_date")

    if start_date:                              #if the user enters in a start_date

        print start_date

        start_date_formatted = datetime.strptime(start_date,"%Y-%m-%d") #reformat start and end dates as date objects
        end_date_formatted = datetime.strptime(end_date,"%Y-%m-%d")
        
        return Crime_Stat.get_features_objects_by_date(start_date_formatted,end_date_formatted) #call class method that will return GeoJSON features

    else:                               # user has not entered in a date, use a default period
        
        end_date = datetime.now()                    
        start_date = end_date - timedelta(days=15)

        print start_date

        return Crime_Stat.get_features_objects_by_date(start_date,end_date)


@app.route('/organizations')
def show_organization_form():
    """Shows form for organizations/NGOs to complete."""
   
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

    categories = str(request.args.get("categories")) #put JS returned into string
    categories_list = categories.strip("]").strip("[").split(",") #put string into list
    category_list = []

    for category in categories_list:    #iterate through the list to strip out quotes and add to a list
        category_stripped = category.strip('"')
        category_list.append(category_stripped)


@app.route('/twitter_auth', methods=["GET"])
def get_oauth_token():

    # Example using callback (web app)
    verifier = request.args.get('oauth_verifier')
    # verifier = auth.request_token["oauth_token"]

    print verifier

    # Let's say this is a web app, so we need to re-build the auth handler
    # first...
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    token = session.get('request_token')
    session.clear()
    # session.delete('request_token')
    auth.request_token = token

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print 'Error! Failed to get access token.'

    token = auth.access_token
    secret = auth.access_token_secret

    print token
    print secret

    # Construct the API instance
    api = tweepy.API(auth)


@app.route('/twitter_signin')
def twitter_auth():
    """Twitter authorization."""

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret,"https://isafe.herokuapp.com/twitter_auth")

    # Redirect user to Twitter to authorize
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print 'Error! Failed to get request token.'

    session.setdefault('request_token', auth.request_token)

    print auth.request_token["oauth_token"]

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