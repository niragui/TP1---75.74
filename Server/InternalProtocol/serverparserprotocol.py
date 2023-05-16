import json
import datetime
import csv

from trip import Trip
from weather import Weather
from station import Station
from point import Point
from common import int_to_bytes, int_from_bytes, INT_LENGTH
from constants import STOP_TYPE

ENCODING = "utf-8"

TRIP_START = -1
TRIP_TYPE = 1
WEATHER_TYPE = 2
STATION_TYPE = 3

TRIP_LENGTH = 7
WEATHER_LENGTH_MONTREAL = 21
WEATHER_LENGTH = 20
STATION_LENGTH = 5

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class Message():
    def __init__(self, type, lines, city):
        self.type = type
        self.content = {}
        self.content.update({"City": city})
        self.content.update({"Lines": lines})

    def create_message(self):
        bytes = b""
        type_byted = int_to_bytes(self.type)
        bytes += type_byted

        string_json = json.dumps(self.content).encode(ENCODING)

        bytes += string_json

        return bytes


def parse_trips(data, city):
    if len(data[0]) != TRIP_LENGTH:
        raise Exception(f"Data Read From Line ({len(data[0])}) Not Correct Length For Trip ({TRIP_LENGTH}) in {city}")

    trips = []

    for data_trip in data:
        start_time = data_trip[0]
        start_time = datetime.datetime.strptime(start_time, TIME_FORMAT)
        start_station = data_trip[1]
        end_time = data_trip[2]
        end_time = datetime.datetime.strptime(end_time, TIME_FORMAT)
        end_station = data_trip[3]
        year_id = data_trip[6]
        start_station += "-"+year_id
        end_station += "-"+year_id

        trip = Trip(start_station, end_station, start_time, end_time, city)
        trips.append(trip)

    return trips


def parse_stations(data, city):
    if len(data[0]) != STATION_LENGTH:
        raise Exception(f"Data Read From Line ({len(data[0])}) Not Correct Length For Station ({STATION_LENGTH}) in {city}")

    stations = []

    for data_station in data:
        code = data_station[0]
        year_id = data_station[4]
        code += "-"+year_id
        name = data_station[1]
        if len(data_station[2]) == 0:
            latitude = 0
        else:
            latitude = float(data_station[2])

        if len(data_station[3]) == 0:
            longitude = 0
        else:
            longitude = float(data_station[3])

        location = Point(latitude, longitude)

        station = Station(code, name, location, city)
        stations.append(station)

    return stations


def parse_weathers(data, city):
    if city != "Montreal" and len(data[0]) != WEATHER_LENGTH:
        raise Exception(f"Data Read From Line ({len(data[0])}) Not Correct Length For Weather ({WEATHER_LENGTH}) in {city}")

    if city == "Montreal" and len(data[0]) != WEATHER_LENGTH_MONTREAL:
        raise Exception(f"Data Read From Line ({len(data[0])}) Not Correct Length For Weather ({WEATHER_LENGTH_MONTREAL})")

    weathers = []

    for data_weather in data:
        date = data_weather[0]
        date = datetime.datetime.strptime(date, DATE_FORMAT).date()
        try:
            prec_tot = float(data_weather[1])
        except:
            raise Exception(f"Error Casting {city}-{date}")

        weather = Weather(date, prec_tot, city)
        weathers.append(weather)

    return weathers


def parse_message_line(lines, type, city):
    reader = csv.reader(lines)
    data = []
    for row in reader:
        data.append(row)

    try:
        if type == TRIP_TYPE:
            return TRIP_TYPE, parse_trips(data, city)
        elif type == STATION_TYPE:
            return STATION_TYPE, parse_stations(data, city)
        elif type == WEATHER_TYPE:
            return WEATHER_TYPE, parse_weathers(data, city)
        elif type == STOP_TYPE:
            return STOP_TYPE, STOP_TYPE
        else:
            raise Exception(f"Type {type} Doesn't Exist")
    except Exception as err:
        raise Exception(f"{err} Rose While Checking {lines}")


def read_message(bytes_read):
    message_type = int_from_bytes(bytes_read[:INT_LENGTH])
    message = json.loads(bytes_read[INT_LENGTH:].decode(ENCODING))

    lines = message.get("Lines")
    city = message.get("City")

    return parse_message_line(lines, message_type, city)

