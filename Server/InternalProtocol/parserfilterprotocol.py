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

TRIP_TYPE = 1
WEATHER_TYPE = 2
STATION_TYPE = 3
FIRST_TRIP = 4

TRIP_LENGTH = 7
WEATHER_LENGTH_MONTREAL = 21
WEATHER_LENGTH = 20
STATION_LENGTH = 5

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class Message():
    def __init__(self, elements, id):
        self.type = self.decide_type(elements)
        self.content = []
        if self.type == STOP_TYPE or self.type == FIRST_TRIP:
            self.content = id
        elif self.type != FIRST_TRIP:
            for element in elements:
                self.content.append(self.make_dic(element))

    def decide_type(self, elements):
        if isinstance(elements, int) and elements == FIRST_TRIP:
            return FIRST_TRIP
        elif isinstance(elements, int) and elements == STOP_TYPE:
            return STOP_TYPE
        else:
            element = elements[0]
            if isinstance(element, Trip):
                return TRIP_TYPE
            elif isinstance(element, Station):
                return STATION_TYPE
            else:
                return WEATHER_TYPE

    def make_dic(self, element):
        values = vars(element)
        ret_values = {}

        for key, value in values.items():
            if isinstance(value, datetime.date):
                value = value.isoformat()
            if isinstance(value, datetime.datetime):
                value = value.strftime(TIME_FORMAT)
            if isinstance(value, Point):
                ret_values.update({"latitude": value.latitude})
                ret_values.update({"longitude": value.longitude})
                continue
            ret_values.update({key: value})

        return ret_values

    def create_message(self):
        bytes = b""
        type_byted = int_to_bytes(self.type)
        bytes += type_byted

        string_json = json.dumps(self.content).encode(ENCODING)

        bytes += string_json
        print(f"Sending: {self.type}{self.content}")

        return bytes


def parse_trips(data):
    trips = []

    for data_trip in data:
        start_time = data_trip.get("begin")
        start_time = datetime.datetime.strptime(start_time, TIME_FORMAT)
        start_station = data_trip.get("start")
        end_time = data_trip.get("end")
        end_time = datetime.datetime.strptime(end_time, TIME_FORMAT)
        end_station = data_trip.get("finish")
        city = data_trip.get("city")

        trip = Trip(start_station, end_station, start_time, end_time, city)
        trips.append(trip)

    return trips


def parse_stations(data):
    stations = []

    for data_station in data:
        code = data_station.get("code")
        name = data_station.get("name")
        latitude = data_station.get("latitude")
        longitude = data_station.get("longitude")
        city = data_station.get("city")

        location = Point(latitude, longitude)

        station = Station(code, name, location, city)
        stations.append(station)

    return stations


def parse_weathers(data):
    weathers = []

    for data_weather in data:
        date = data_weather.get("date")
        date = datetime.date.fromisoformat(date)
        prec_tot = data_weather.get("prec_tot")
        city = data_weather.get("city")

        weather = Weather(date, prec_tot, city)
        weathers.append(weather)

    return weathers


def parse_message_line(elements, type):
    try:
        if type == TRIP_TYPE:
            return TRIP_TYPE, parse_trips(elements)
        elif type == STATION_TYPE:
            return STATION_TYPE, parse_stations(elements)
        elif type == WEATHER_TYPE:
            return WEATHER_TYPE, parse_weathers(elements)
        elif type == STOP_TYPE:
            return STOP_TYPE, STOP_TYPE
        elif type == FIRST_TRIP:
            return FIRST_TRIP, FIRST_TRIP
        else:
            raise Exception(f"Type {type} Doesn't Exist")
    except Exception as err:
        raise Exception(f"{err} Rose While Checking {elements}")


def read_message(bytes_read):
    message_type = int_from_bytes(bytes_read[:INT_LENGTH])
    elements = json.loads(bytes_read[INT_LENGTH:].decode(ENCODING))

    return parse_message_line(elements, message_type)
