from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

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
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

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
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
)


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    # Locate the last date in the dataset

    # Calculate the date 1 year ago from the last data point in the database
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    last_year_prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date, Measurement.prcp != None).\
        order_by(Measurement.date).all()


    return jsonify(last_year_prcp)


@app.route("/api/v1.0/stations")
def stations():
    station_count = session.query(Station.id).count()
    sel = [Measurement.station, func.count(Measurement.id)]

    station_active = session.query(*sel).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).all()

    return jsonify(station_active)


@app.route("/api/v1.0/tobs")
def tobs():
# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.

    query_date_tobs = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    last_year_tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= query_date_tobs, Measurement.prcp != None).\
        order_by(Measurement.date).all()

    return jsonify(last_year_tobs)


@app.route("/api/v1.0/<start>")
def start_date(start):
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

    return jsonify(session.query(func.min(Measurement.date),func.max(Measurement.date),\
        func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all())

@app.route("/api/v1.0/<start>/<end>") 
def tobs_by_date_range(start, end):
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

        return jsonify(session.query(func.min(Measurement.date),func.max(Measurement.date),\
        func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all())

if __name__ == '__main__':
    app.run(debug=True)
