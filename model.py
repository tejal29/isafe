"""Models and database functions for ISafe."""

from flask_sqlalchemy import SQLAlchemy
import decimal
from datetime import datetime
from flask import jsonify
import os
from time import time
from sqlalchemy import Index, ForeignKey

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class DM_detail(db.Model):

	"""Table of data from direct messages."""

	__tablename__ = "dm_details"

	incident_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, nullable=False)
	location = db.Column(db.String(60), nullable=False)
	x_cord = db.Column(db.Numeric, nullable=True)
	y_cord = db.Column(db.Numeric, nullable=True)
	day_of_week = db.Column(db.String(10), nullable=True)
	datetime = db.Column(db.Date, nullable=False)
	month = db.Column(db.String(10), nullable=True)
	time = db.Column(db.Time, nullable=True)
	hour = db.Column(db.String(10), nullable=True)
	category = db.Column(db.String(60), nullable=True)
	raw_text = db.Column(db.String(140), nullable=False)
	data_source = db.Column(db.String(60), nullable=True)
	to_safety = db.Column(db.String(60), nullable=False)

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
							  "title": self.category,
							  "description": self.raw_text, #put description in string and called title capitalization on it
							  "date": date_formatted,
							  "time":time_formatted,
							  "address":self.address,
							  "marker-color": marker_color_dict[self.category], #use marker color dictionary to assign marker colors based on type of crime
							  "marker-size": "small",
							  "marker-symbol": "marker"
							}
						  }

		return feature_object

	@classmethod
	def get_features_objects_by_date(cls,start_date,end_date):
		"""Query table and then make feature objects on each instance to be sent to map"""

		incidents = cls.query.filter(cls.date >= start_date, cls.date <= end_date).all() #create query object of rows that fall in time range

		print len(crime_stats)
		
		marker_object_dict = { "type": "FeatureCollection"}
		marker_object_list = []

		for incident in incidents:                               #iterate over query object calling the feature object class method on each
			marker_object = incident.make_feature_object()

			marker_object_list.append(marker_object)            #append each feature object to a list  

		marker_object_dict["features"] = marker_object_list     #add list of feature objects to the value of a key

		return jsonify(marker_object_dict)

class NGO(db.Model):

	"""Table of NGO information."""

	__tablename__ = "ngo_info"

	org_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	org_name = db.Column(db.String(60), nullable=False)
	name = db.Column(db.String(60), nullable=False)
	twitter_handle = db.Column(db.String(60), nullable=False)
	email = db.Column(db.String(60), nullable=False)
	phone = db.Column(db.String(60), nullable=False)
	x_cord = db.Column(db.Numeric, nullable=False)
	y_cord = db.Column(db.Numeric, nullable=False)
	address = db.Column(db.String(60), nullable=False)
	description = db.Column(db.String(500), nullable=False)
	category = db.Column(db.String(60), nullable=False)
	twitter_user_id = db.Column(db.String(60), nullable=True, unique=True)
	twitter_user_token = db.Column(db.String(60), nullable=True)
	twitter_user_secret = db.Column(db.String(60), nullable=True)


	def make_feature_object(self):
		"""Make GeoJSON feature object"""

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
								  "title": self.category,
								  "description": self.description, #put description in string and called title capitalization on it
								  "date": date_formatted,
								  "time":time_formatted,
								  "address":self.address,
								  "marker-color": marker_color_dict[self.category], #use marker color dictionary to assign marker colors based on type of crime
								  "marker-size": "small",
								  "marker-symbol": "marker"
								}
							  }

		return feature_object

	@classmethod
	def get_features_objects(cls):
		"""Query table and then make feature objects on each instance to be sent to map"""

		organizations = cls.query.all() #create query object of rows that fall in time range

		print len(crime_stats)
		
		marker_object_dict = { "type": "FeatureCollection"}
		marker_object_list = []

		for organization in organizations:                               #iterate over query object calling the feature object class method on each
			marker_object = organization.make_feature_object()

			marker_object_list.append(marker_object)            #append each feature object to a list  

		marker_object_dict["features"] = marker_object_list     #add list of feature objects to the value of a key

		return jsonify(marker_object_dict)

class Connection(db.Model):

	"""Table of connection/counseling status information."""

	__tablename__ = "connection_status"

	connection_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.String(60), nullable=False)
	NGO_id = db.Column(db.String(60), db.ForeignKey('ngo_info.twitter_user_id'), nullable=False)
	description = db.Column(db.String(60), nullable=False)
	status_code = db.Column(db.String(60), nullable=False)
	category = db.Column(db.String(60), nullable=False)

class Category(db.Model):

	"""Table of category information."""

	__tablename__ = "category_info"

	category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	category = db.Column(db.String(60), nullable=False)
	category_description = db.Column(db.String(60), nullable=False)

class Status(db.Model):

	"""Table of status codes."""

	__tablename__ = "status_codes"

	status_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	status_code = db.Column(db.String(60), nullable=False)
	status_description = db.Column(db.String(60), nullable=False)

##############################################################################
# Helper functions

def connect_to_db(app):
	"""Connect the database to our Flask app."""

	# Configure to use our PostgreSQL database
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "postgresql://localhost/isafe_db")
	db.app = app
	db.init_app(app)
        db.create_all()

if __name__ == "__main__":
	# As a convenience, if we run this module interactively, it will leave
	# you in a state of being able to work with the database directly.

	from server import app
	connect_to_db(app)
	print "Connected to DB."
