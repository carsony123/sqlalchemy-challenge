# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:////Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Flask setup
app = Flask(__name__)

# Flask routes
@app.route("/")
def home():
    # List all available api routes
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Return the precipitation data for the last 12 months
    last_year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation_data = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= last_year_date)
        .order_by(Measurement.date)
        .all()
    )
    precipitation_dict = {}
    for result in precipitation_data:
        precipitation_dict[result[0]] = result[1]
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Return a list of stations from the dataset
    station_data = session.query(Station.name, Station.station).all()
    station_list = []
    for result in station_data:
        station_list.append({"Name": result[0], "Station": result[1]})
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Return the temperature observation data for the most active station for the last 12 months
    last_year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_active_station = (
        session.query(Measurement.station, func.count(Measurement.station))
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()[0]
    )
    temperature_data = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == most_active_station)
        .filter(Measurement.date >= last_year_date)
        .all()
    )
    temperature_list = []
    for result in temperature_data:
        temperature_list.append({"Date": result[0], "Temperature": result[1]})
    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
def temp_range_start(start):
    # Query the database
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    # Close the session
    session.close() 
    # Convert the query results to a list
    temp_stats_list = list(np.ravel(temp_stats))
    
    # Return the JSON representation of the list
    return jsonify(temp_stats_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start, end):
    # Query the database
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Close the session
    session.close()
    
    # Convert the query results to a list
    temp_stats_list = list(np.ravel(temp_stats))
    
    # Return the JSON representation of the list
    return jsonify(temp_stats_list)
