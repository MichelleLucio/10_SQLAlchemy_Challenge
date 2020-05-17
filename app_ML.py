import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
measurement = Base.classes.measurement
Station = Base.classes.station


#flask setup
app = Flask(__name__)

#flask routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date/<start><br/>"
        f"/api/v1.0/datesearch/<start2><end2><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates & precipitation"""
    # Query all stations & dates
    precip_results = session.query(measurement.date, measurement.prcp).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_precip = []
    for result in precip_results:
        precip_dict = {}
        precip_dict["date"] = result[0]
        precip_dict["prcp"] = result[1]
        all_precip.append(precip_dict)

    return jsonify(all_precip)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all stations
    station_results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    #convert list of tuples into normal list
    all_station = list(np.ravel(station_results))

    return jsonify(all_station)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of tobs for last year"""
    # Query station with most observations
    most_station = "USC00519281"
    year_ago = (dt.datetime(2017, 8, 23)) - dt.timedelta(days=366)
    tobs_results = session.query(measurement.date, measurement.tobs).filter(measurement.station ==most_station).filter(measurement.date >= year_ago).all()
    session.close()

    #convert list of tuples into normal list
    all_tobs = list(np.ravel(tobs_results))

    return jsonify(all_tobs)


@app.route("/api/v1.0/start date/<start>")
def start_date_temps(start):
    """Fetch the tobs for dates >= start date or a 404 if not."""
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        #end_date (string): A date string in the format %Y-%m-%d       
    Returns:
        TMIN, TAVE, and TMAX
    """
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    start_temp_results = (session.query(*sel)\
        .filter(func.strftime("%Y-%m-%d", measurement.date) >= start)\
        .group_by(measurement.date).all())
    
    session.close()

    # Create a dictionary from the row data 
    start_temps = []
    for result in start_temp_results:
        start_temps_dict = {}
        start_temps_dict["Date"] = result[0]
        start_temps_dict["Low Temp"] = result[1]
        start_temps_dict["Average Temp"] = result[2]
        start_temps_dict["High Temp"] = result[3]
        start_temps.append(start_temps_dict)

    return jsonify(start_temps)


@app.route("/api/v1.0/datesearch/<start2>/<end2>")
def start_end(start2, end2):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    start_end_results = (session.query(*sel)\
        .filter(func.strftime("%Y-%m-%d", measurement.date) >= start2)\
        .filter(func.strftime("%Y-%m-%d", measurement.date) <= end2)\
        .group_by(measurement.date).all())
    
    session.close()

    # Create a dictionary from the row data 
    st_end_temps = []
    for result in start_end_results:
        temps_dict = {}
        temps_dict["Date"] = result[0]
        temps_dict["Low Temp"] = result[1]
        temps_dict["Average Temp"] = result[2]
        temps_dict["High Temp"] = result[3]
        st_end_temps.append(temps_dict)

    return jsonify(st_end_temps)


if __name__ == '__main__':
    app.run(debug=True)