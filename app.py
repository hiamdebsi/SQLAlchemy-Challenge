#Import dependencies 
import numpy as np
import pandas as pd
import time
import datetime as dt
import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify

#####################################################
#Setting up the database
#####################################################

#Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect = True)

#Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

#Create our session (link) from python to the DB
session = Session(engine)

#####################################################
#Flask Setup
#####################################################
app = Flask(__name__)

#####################################################
#Flask Routes
#####################################################

#Welcome Page
@app.route("/")
def welcome():
    #List all available api routes
    return(
        f"List of all Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature: /api/v1.0/tobs<br/>"
        f"Start Date: /api/v1.0/<start><br/>"
        f"Start-End Range: /api/v1.0/<start>/<end>"
    )

####################################################
#Precipitation Route 
####################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Will return a list of amount of precipitation with dates

    #Query the measurements for the year
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    latest_date = session.query(measurement.date).\
        order_by(measurement.date.desc()).first().date

    year_precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date>=previous_year).\
        filter(measurement.date<=latest_date).\
        order_by(measurement.date).all()
    
    #Create a dict with date as the key, and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in year_precipitation}

    return jsonify(precipitation_dict)
####################################################
#Stations Route 
####################################################
@app.route("/api/v1.0/stations")
def stations():
    #Will return a list of all the stations
    stations=session.query(station.station).all()
    #Conver data into list
    stations_list=list(np.ravel(stations))
    return jsonify(stations_list)

####################################################
#Temperature Route 
####################################################
@app.route("/api/v1.0/tobs")
def temperature():
    #Most active stations query
    most_active_stations = session.query(measurement.station,func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).\
        all()
    
    #Query the last 12 months of temp observation for the most active station
    top_station = most_active_stations[0][0]

    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    temp_obs = session.query(measurement.station, measurement.date, measurement.tobs).\
        filter(measurement.station == top_station).\
        filter(measurement.date > previous_year).\
        order_by(measurement.date.desc()).all()

    #Convert data into a list
    temp_list=list(np.ravel(temp_obs))
    
    return jsonify(temp_list)

####################################################
#Start and End Dates Route 
####################################################
@app.route("/api/v1.0/<start>")
def start_date_only(start):
    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date>=start).\
        all()
    temp_results = list(np.ravel(results))
    return jsonify(temp_results)

@app.route("/api/v1.0/<start><end>")
def start_end_date(start,end):
    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date>=start).\
        filter(measurement.date<=end).\
        all()
    temp_results = list(np.ravel(results))
    return jsonify(temp_results)

if __name__ == "__main__":
    app.run(debug=True)



