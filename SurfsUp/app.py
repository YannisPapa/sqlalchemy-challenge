# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
# in class we learned that it is better to start and close sessions only when being used
# so i moved this into each section below
# session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Functions
#################################################

# Function to find the first date in the data
def first_date():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the first date found in the data
    found_date = session.query(func.min(Measurement.date))

    # Close the session
    session.close()

    return found_date[0][0]

# Function to find the last date in the data
def last_date():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the last date found in the data
    found_date = session.query(func.max(Measurement.date))

    # Close the session
    session.close()

    return found_date[0][0]

# Function to find what day is a year before the last date in the data
def last_year():
    # Find the most recent date
    last_date_found = last_date()
    # Calculate the last 12 months from most recent date
    last_twelve_months = pd.to_datetime(last_date_found).date() - dt.timedelta(days=365)

    return last_twelve_months

# Function to find the most active station and retunr it
def most_active_station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Build the list of all stations based on how active they are (how many times they show up in the database)
    most_active_stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    # Close the session
    session.close()

    return most_active_stations[0][0]

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""

    # Find the first date and last date found in the data to be used as an example
    last_date_found = last_date()
    first_date_found = first_date()

    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/{first_date_found}<br/>"
        f"/api/v1.0/{first_date_found}/{last_date_found}"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns a list of precipitation for every date in the last 12 months from most recent date, sort it by date"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get all the dates and prcp's for every date in the last 12 months from most recent date, sort it by date
    prcp_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year()).order_by(Measurement.date).all()

    # Close the session
    session.close()

    # Build a list of dictionary's containing all the dates and the prcp for those dates
    prcp_list = []
    for date, precipitation in prcp_results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = precipitation
        prcp_list.append(prcp_dict)

    # Return the list JSONified
    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    """Returns a list of all stations and their information"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get the list of all stations and their information
    all_stations = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()

    # Close the session
    session.close()

    # Build a list of dictionary's containing all the info for each station
    station_list = []
    for station,name,latitude,longitude,elevation in all_stations:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_dict["Elevation"] = elevation
        station_list.append(station_dict)

    # Return the list JSONified
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Returns a list of date and tobs for the most active station over that last 12 months"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get the date and tobs for the most active station over that last 12 months
    tobs_results = session.query(Measurement.date, Measurement.tobs).where(Measurement.station == most_active_station()).filter(Measurement.date >= last_year()).order_by(Measurement.date).all()

    # Close the session
    session.close()

    # Build a list of dictionary's containing dates and tobs from the most active station over that last 12 months
    tobs_list = []
    for date, temperature in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = temperature
        tobs_list.append(tobs_dict)

    # Return the list JSONified
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Returns a list of min temp, avg temp, and max temp from a specified start date to the most current date"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get the min temp, avg temp, and max temp from a specified start date to the most current date
    tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).where(Measurement.date >= start).all()

    # Close the session
    session.close()

    # Build a list of dictionary's containing min temp, avg temp, and max temp for the specified date range
    tobs_list = []
    for tmin, tavg, tmax in tobs_results:
        tobs_dict = {}
        tobs_dict["TMIN"] = tmin
        tobs_dict["TAVG"] = tavg
        tobs_dict["TMAX"] = tmax
        tobs_list.append(tobs_dict)

    # Return the list JSONified
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Returns a list of min temp, avg temp, and max temp from a specified start date to a specified end date"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get the min temp, avg temp, and max temp from a specified start date to a specified end date
    tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).where((Measurement.date >= start) & (Measurement.date <= end)).all()

    # Close the session
    session.close()

    # Build a list of dictionary's containing min temp, avg temp, and max temp for the specified date range
    tobs_list = []
    for tmin, tavg, tmax in tobs_results:
        tobs_dict = {}
        tobs_dict["TMIN"] = tmin
        tobs_dict["TAVG"] = tavg
        tobs_dict["TMAX"] = tmax
        tobs_list.append(tobs_dict)

    # Return the list JSONified
    return jsonify(tobs_list)

if __name__ == '__main__':
    app.run(debug=True)