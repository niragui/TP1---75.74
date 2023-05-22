import pika

from serverparserprotocol import read_message, TRIP_TYPE, STATION_TYPE, WEATHER_TYPE
from parserfilterprotocol import FIRST_TRIP, Message
from constants import STOP_TYPE
from trip import Trip
from weather import Weather
from station import Station

from rabbitconnection import RabbitConnection

RAIN_QUEUE = "rain_trips_queue"
MONTREAL_QUEUE = "montreal_trips_queue"
YEAR_QUEUE = "year_trips_queue"

STATIONS_EXCHANGE = "stations"
WEATHER_EXCHANGE = "weathers"

RAIN_FILTERS = 3
MONTREAL_FILTERS = 3
YEAR_FILTERS = 3

DATA_QUEUE = "data_queue"


class Parser():
    def __init__(self, pars_id, rains=RAIN_FILTERS, montreals=MONTREAL_FILTERS, years=YEAR_FILTERS):
        self.rain_filters = rains
        self.montreal_filters = montreals
        self.year_filters = years
        self.first_trip_sent = False
        self.connection = RabbitConnection()
        self.id = pars_id

        self.data_queue = self.connection.create_queue_receiver(queue_name=DATA_QUEUE)
        self.stations_queue = self.connection.create_queue_sender(exchange=STATIONS_EXCHANGE)
        self.weather_queue = self.connection.create_queue_sender(exchange=WEATHER_EXCHANGE)

        self.rain_queue = self.connection.create_queue_sender(queue_name=RAIN_QUEUE)
        self.montreal_queue = self.connection.create_queue_sender(queue_name=MONTREAL_QUEUE)
        self.year_queue = self.connection.create_queue_sender(queue_name=YEAR_QUEUE)

    def process_trip(self, trips):
        if not self.first_trip_sent:
            print("First Trip Announcement Sent")
            message = Message(FIRST_TRIP, self.id)
            bytes_message = message.create_message()
            self.stations_queue.send(bytes_message)
            self.weather_queue.send(bytes_message)
            self.first_trip_sent = True

        message = Message(trips, self.id)
        bytes_message = message.create_message()

        self.rain_queue.send(bytes_message)
        self.montreal_queue.send(bytes_message)
        self.year_queue.send(bytes_message)

    def process_station(self, stations):
        message = Message(stations, self.id)
        bytes_message = message.create_message()
        self.stations_queue.send(bytes_message)

    def process_weather(self, weathers):
        message = Message(weathers, self.id)
        bytes_message = message.create_message()
        self.weather_queue.send(bytes_message)

    def publish_stops(self):
        message = Message(STOP_TYPE, self.id)
        bytes_message = message.create_message()
        for _ in range(self.rain_filters):
            self.rain_queue.send(bytes_message)
        for _ in range(self.montreal_filters):
            self.montreal_queue.send(bytes_message)
        for _ in range(self.year_filters):
            self.year_queue.send(bytes_message)

    def add_data(self, body_read):
        ent_type, entity_to_process = read_message(body_read)

        if ent_type == TRIP_TYPE:
            self.process_trip(entity_to_process)
        elif ent_type == STATION_TYPE:
            self.process_station(entity_to_process)
        elif ent_type == WEATHER_TYPE:
            self.process_weather(entity_to_process)
        elif ent_type == STOP_TYPE:
            self.publish_stops()
            self.data_queue.close()
        else:
            raise Exception(f"Type Received Don't Make Sense {ent_type}")

    def run(self):
        self.data_queue.receive(self.add_data)
        self.connection.close()
