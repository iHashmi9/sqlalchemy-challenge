# Import the dependencies.
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables
Base.classes.keys()

# Save references to each table
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
def home():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Precipitation data for the last 12 months<br/>"
        f"/api/v1.0/stations - List of stations<br/>"
        f"/api/v1.0/tobs - Temperature observations for the most active station in the last year<br/>"
        f"/api/v1.0/<start> - Temperature statistics (TMIN, TAVG, TMAX) from a start date<br/>"
        f"/api/v1.0/<start>/<end> - Temperature statistics (TMIN, TAVG, TMAX) for a date range"
    )

# Define the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)

    # Query and convert precipitation data to a dictionary
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    precipitation_dict = []

    for date, prcp in precipitation_data:
        entry = {
            "date": date,
            "prcp": prcp
        }
        precipitation_dict.append(entry)

    return jsonify(precipitation_dict)

# Define the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query the list of stations
    stations_list = session.query(Station.station, Station.name).all()

    # Create a dictionary with station names as keys and station IDs as values
    stations_dict = []

    for station_id, station_name in stations_list:
        station_entry = {
            "station_id": station_id,
            "station_name": station_name
        }
        stations_dict.append(station_entry)

    return jsonify(stations_dict)

# Define the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)) \
        .group_by(Measurement.station) \
        .order_by(func.count(Measurement.station).desc()) \
        .first()[0]

    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)

    # Query temperature observations for the most active station in the last year
    tobs_data = session.query(Measurement.date, Measurement.tobs) \
        .filter(Measurement.station == most_active_station) \
        .filter(Measurement.date >= one_year_ago) \
        .all()

    # Convert the data to a list of dictionaries
    tobs_dict = []

    for date, temperature in tobs_data:
        entry = {
            "date": date,
            "temperature": temperature
        }
        tobs_dict.append(entry)

    return jsonify(tobs_dict)

# Define the /api/v1.0/<start> route
@app.route("/api/v1.0/<start>")
def temp_start(start):
    # Query and calculate temperature statistics for a specified start date
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
        .filter(Measurement.date >= start) \
        .all()

    return jsonify(temperature_stats)

# Define the /api/v1.0/<start>/<end> route
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):
    # Query and calculate temperature statistics for a specified date range
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
        .filter(Measurement.date >= start) \
        .filter(Measurement.date <= end) \
        .all()

    return jsonify(temperature_stats)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)