"""Utility file to seed crime statistics and victim data"""

from model import DM_detail, NGO, Connection, Category, Status, connect_to_db, db
from server import app
import csv
from datetime import datetime
from sqlalchemy import desc
import requests
import json


def load_category_table():

	"""Fill category table."""


def load_status_table():

	"""Load status code table."""

	



if __name__ == "__main__":
    connect_to_db(app)

    load_category_table()
    load_status_table()