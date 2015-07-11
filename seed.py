"""Utility file to seed crime statistics and victim data"""

from model import Crime_Stat, Data_Import, Hour_Count, Day_Count, Month_Count, connect_to_db, db
from server import app
import csv
from datetime import datetime
from sqlalchemy import desc
import requests
import json


if __name__ == "__main__":
    connect_to_db(app)

    #load_crime_stats()
    load_recent_stats()
    #load_crime_counts()