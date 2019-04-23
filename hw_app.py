# imports
from flask import Flask, jsonify

import numpy as np
import pandas as pd

import datetime as dt
from datetime import datetime as dt_1

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Date stuff
date_frmt = '%Y-%m-%d'
last_date = dt_1.strptime(str(session.query(func.max(Measurement.date)).first()[0]), date_frmt)
delta_days = 365

earliest_date = last_date - dt.timedelta(days=delta_days)

last_date_str = dt_1.strftime(last_date, date_frmt)
earliest_date_str = dt_1.strftime(earliest_date, date_frmt)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
    return f"""<h1>Welcome to the Hawaii Weather API!</h1></br></br>
    <h3>Here is a list of available routes:</h3>
    /api/v1.0/precipitation</br>
    /api/v1.0/stations</br>
    /api/v1.0/tobs</br></br>
    <em>The following routes take dates between {earliest_date_str} and {last_date_str} in the given format:</em></br></br>
    /api/v1.0/YYYY-mm-dd/</br>
    /api/v1.0/YYYY-mm-dd/YYYY-mm-dd
    """

@app.route("/api/v1.0/precipitation")
def prcp():
    results = session.query(Measurement.date, func.sum(Measurement.prcp)).group_by(Measurement.date).all()

    prcp_dict = {}
    for date, prcp in results:
        prcp_dict[date] = prcp

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    
    sel = [Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]

    results = session.query(*sel).all()

    station_list = []
    for st_id, station, name, lat, lng, elev in results:
        station_dict = {}
        station_dict["id"] = st_id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = lat
        station_dict["longitude"] = lng
        station_dict["elevation"] = elev
        station_list.append(station_dict)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results = session.query(*sel).group_by(Measurement.date).filter(Measurement.date >= earliest_date).all()

    tobs_list = []
    for date, tmin, tavg, tmax in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['temp min'] = tmin
        tobs_dict['temp avg'] = tavg
        tobs_dict['temp max'] = tmax
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end=last_date_str):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results = session.query(*sel).group_by(Measurement.date).\
        filter((Measurement.date >= start)&(Measurement.date <= end)).all()

    spec_tobs_list = []
    for date, tmin, tavg, tmax in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['temp min'] = tmin
        tobs_dict['temp avg'] = tavg
        tobs_dict['temp max'] = tmax
        spec_tobs_list.append(tobs_dict)

    return jsonify(spec_tobs_list)
                 
if __name__ == "__main__":
    app.run(debug=True)