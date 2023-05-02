import json
import datetime
import csv

from .trip import Trip
from .weather import Weather
from .station import Station
from .point import Point
from .common import int_to_bytes, int_from_bytes, INT_LENGTH
from .constants import STOP_TYPE

ENCODING = "utf-8"

TRIP_TYPE = 1
WEATHER_TYPE = 2
STATION_TYPE = 3

TRIP_LENGTH = 7
WEATHER_LENGTH = 10
STATION_LENGTH = 5

TIME_FORMAT = "%m/%d/%Y %H:%M"
DATE_FORMAT = "%m/%d/%Y"


class Message():
    def __init__(self, type, line, city):
        self.type = type
        self.contet = {}
        self.content.update({"City": city})
        self.contet.update({"Line": line})

    def create_message(self):
        bytes = b""
        type_byted = int_to_bytes(self.type)
        bytes += type_byted

        string_json = json.dumps(self.contet).encode(ENCODING)

        bytes += string_json

        return bytes


def parse_trip(data, stations, city):
    if len(data) != TRIP_LENGTH:
        raise Exception("Data Read From Line Not Correct Length For Trip")

    start_time = data[0]
    start_time = datetime.datetime.strptime(start_time, TIME_FORMAT)
    start_station = data[1]
    start_id = f"{city}-{start_station}"
    start_station = stations.get(start_id)
    end_time = data[2]
    end_time = datetime.datetime.strptime(end_time, TIME_FORMAT)
    end_station = data[3]
    end_id = f"{city}-{end_station}"
    end_station = stations.get(end_id)

    trip = Trip(start_station, end_station, start_time, end_time, city)

    return trip


def parse_station(data, city):
    if len(data) != STATION_LENGTH:
        raise Exception("Data Read From Line Not Correct Length For Station")

    code = data[0]
    name = data[1]
    latitude = float(data[2])
    longitude = float(data[3])
    location = Point(latitude, longitude)

    station = Station(code, name, location, city)

    return station


def parse_weather(data, city):
    if len(data) != WEATHER_LENGTH:
        raise Exception("Data Read From Line Not Correct Length For Weather")

    date = data[0]
    date = datetime.strptime(date, DATE_FORMAT).date()
    prec_tot = float(data[1])

    weather = Weather(date, prec_tot, city)

    return weather


def parse_message_line(line, type, stations, city):
    reader = csv.reader([line])
    data = []
    for row in reader:
        data = row

    if type == TRIP_TYPE:
        parse_trip(data, stations, city)
    elif type == STATION_TYPE:
        parse_station(data, city)
    elif type == WEATHER_TYPE:
        parse_weather(data, city)
    elif type == STOP_TYPE:
        return STOP_TYPE


def read_message(bytes_read, stations):
    message_type = int_from_bytes(bytes_read[:INT_LENGTH])
    message = json.loads(bytes_read[INT_LENGTH:].decode(ENCODING))

    line = message.get("Line")
    city = message.get("City")

    return parse_message_line(line, message_type, stations, city)

