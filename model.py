"""Models and database functions for final project."""

from flask_sqlalchemy import SQLAlchemy
import decimal
from datetime import datetime
from flask import jsonify
from time import time
from sqlalchemy import Index

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class Crime_Stat(db.Model):

    """Table of crime statistics."""

    __tablename__ = "crime_stats"
    
    incident_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    incident_num = db.Column(db.String(60), nullable=True) #want this to be nullable for citizen report
    data_source = db.Column(db.String(60), nullable=False) #distinguishes between citizen report and official report
    category = db.Column(db.String(60), nullable=True)     #want this to be nullable for citizen report
    map_category = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, nullable=False)
    month = db.Column(db.String(10), nullable=False)
    time = db.Column(db.Time, nullable=False)
    hour = db.Column(db.String(10), nullable=False)
    district = db.Column(db.String(60), nullable=True) #want this to be nullable for citizen report
    address = db.Column(db.String(60), nullable=False)
    x_cord = db.Column(db.Numeric, nullable=False)
    y_cord = db.Column(db.Numeric, nullable=False)

    def make_feature_object(self):
        """Make GeoJSON feature object"""

        date_formatted = datetime.strftime(self.date,"%m/%d/%Y") #format time and date as strings to use in feature objects
        time_formatted = self.time.strftime("%I:%M %p")

        marker_color_dict = {'Personal Theft/Larceny':'#FF0000', #This dictionary will link the type of crime to the color marker it will be assigned    
                                'Robbery':'#0000FF',
                                'Rape/Sexual Assault':'#008000',
                                'Aggravated Assault':'#FFA500',
                                'Simple Assault':'#6600CC',
                                'Other':'#669999',
                            }

        feature_object = {
                                "type": "Feature",
                                "geometry": {
                                  "type": "Point",
                                  "coordinates": [str(decimal.Decimal(self.y_cord)), str(decimal.Decimal(self.x_cord))] #deal with decimal from database
                                },
                                "properties": {
                                  "title": self.map_category,
                                  "description": self.description, #put description in string and called title capitalization on it
                                  "date": date_formatted,
                                  "time":time_formatted,
                                  "address":self.address,
                                  "marker-color": marker_color_dict[self.map_category], #use marker color dictionary to assign marker colors based on type of crime
                                  "marker-size": "small",
                                  "marker-symbol": "marker"
                                }
                              }

        return feature_object

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/isafe_db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."