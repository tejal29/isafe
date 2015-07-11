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


@app.route('/organizations')
def show_organization_form():
    """Shows form for organizations/NGOs to complete."""
   
    return render_template("organization_form.html")

@app.route('/save_org_info')
def process_report():
    """Save reported crime to database."""

    time_input = request.args.get("time")
    date_input = request.args.get("date")
    address_input = request.args.get("address")
    description = request.args.get("description")
    map_category = request.args.get("map_category")


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