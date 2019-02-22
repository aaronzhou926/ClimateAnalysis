
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f" - list of rain totals from all stations<br/>"
        f"/api/v1.0/stations<br/>"
        f"- list of Station numbers and names<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- list of prior year temperatures from all stations<br/>"
        f"/api/v1.0/STARTTIME<br/>"
        f"- When given the start date (yyyy-mm-dd), calculates the min/ave/max temp for all dates greate than and equal to teh start date.<br/>"
        f"/api/v1.0/STARTTIME/ENDTIME<br/>"
        f"- Please provide the start date (yyyy-mm-dd) and end date (yyyy-mm-dd)"
        )

@app.route("/api/v1.0/precipitation")
def percipitation():
    """Return percipitation"""
    # Query all date and prcp from Measurement
    results = session.query(Measurement).all()
    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []

    for result in results:
        stations_dict = {}
        stations_dict["date"] = result.date
        stations_dict["prcp"] = result.prcp
        all_stations.append(stations_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/stations")
def stations():
    """Return Station Names"""
    results = session.query(Station.station, Station.name,).all()
    # Create a dictionary from the row data and append to a list of all_stations
    all_stations=[]
    for result in results:
        stations_dict = {}
        stations_dict["station"] = result[0]
        stations_dict["name"] = result[1]
        all_stations.append(stations_dict)
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    #query for the dates and temps froma year fromt the last data point.
    query_date = dt.date(2017,8,23) - dt.timedelta(weeks=52)
    #create all data from 2016/8/23-2017/8/23
    lasttwelvemonths = (session.query(Measurement)
                   .filter(func.strftime(Measurement.date)>=query_date)
                   .order_by(Measurement.date)
                   .all())
    one_year_tobs=[]

    for last in lasttwelvemonths:
        tobs_dict = {}
        tobs_dict["date"] = last.date
        tobs_dict["tobs"] = last.tobs
        one_year_tobs.append(tobs_dict)

    return jsonify(one_year_tobs)

@app.route("/api/v1.0/<start>")
def trip1(start):

    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),
    func.max(Measurement.tobs)).filter(Measurement.date>=start).all()

    trip = list(np.ravel(trip_data))

    return jsonify(trip)

@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):

    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),
    func.max(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.date<=end).all()

    trip = list(np.ravel(trip_data))

    return jsonify(trip)

if __name__ == '__main__':
    app.run(debug=True)