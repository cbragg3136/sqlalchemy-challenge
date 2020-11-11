#import dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#database setup
connection_string = "sqlite:///../Instructions/Resources/hawaii.sqlite"
engine = create_engine(connection_string)

Base = automap_base()
Base.prepare(engine, reflect=True)

#print(Base.classes.keys())
Measurement = Base.classes.measurement
Station = Base.classes.station

#create app
app = Flask(__name__)

#routes
@app.route("/")
def index():
    return """
        Available routes: <br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>
        /api/v1.0/[start_date]<br/>
        /api/v1.0/[start_date]/[end_date]
    """

#dictionary of prcp/precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Perform a query to retrieve the data and precipitation scores
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).all()
    session.close()
    precipitation = {}
    for date, prcp in prcp_data:
        precipitation[date] = prcp
    return jsonify(precipitation)


#list of stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station).all()
    session.close()

    stations = []   
    for item in results:
        stations_dict = {
        "station": item.station,
        "name": item.name
       }
        stations.append(stations_dict)

    return jsonify(stations)

    
#list of tobs/temperatures for most active station for the last year of data
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    year_temps = session.query(Measurement.tobs, Measurement.date).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= query_date).all()
    session.close()

    tobs = []   
    for temps in year_temps:
        tobs_dict = {
        "date": temps.date,
        "tobs": temps.tobs
       }
        tobs.append(tobs_dict)

    return jsonify(tobs)


#list of `TMIN`, `TAVG`, and `TMAX` after any start date up to the final date in dataset       
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.date).all()
    session.close()
    temp_start = []   
    for result in results:
        temp_dict = {}
        temp_dict['Date'] = result[0]
        temp_dict['TMIN'] = result[1]
        temp_dict['TAVG'] = result[2]
        temp_dict['TMAX'] = result[3]
        temp_start.append(temp_dict)
    return jsonify(temp_start)


#list of `TMIN`, `TAVG`, and `TMAX` between any designated start and end dates
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter( Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    session.close()
    temp_start = []   
    for result in results:
        temp_dict = {}
        temp_dict['Date'] = result[0]
        temp_dict['TMIN'] = result[1]
        temp_dict['TAVG'] = result[2]
        temp_dict['TMAX'] = result[3]
        temp_start.append(temp_dict)
    return jsonify(temp_start)


if __name__ == '__main__':
    app.run(debug=True)
