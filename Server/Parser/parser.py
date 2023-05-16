import pika

from serverparserprotocol import read_message, TRIP_TYPE, STATION_TYPE, WEATHER_TYPE
from parserfilterprotocol import FIRST_TRIP, Message
from constants import STOP_TYPE
from trip import Trip
from weather import Weather
from station import Station

RAIN_QUEUE = "rain_trips_queue"
MONTREAL_QUEUE = "montreal_trips_queue"
YEAR_QUEUE = "year_trips_queue"

STATIONS_EXCHANGE = "stations"
WEATHER_EXCHANGE = "weathers"

RAIN_FILTERS = 3
MONTREAL_FILTERS = 3
YEAR_FILTERS = 3


class Parser():
    def __init__(self, rains=RAIN_FILTERS, montreals=MONTREAL_FILTERS, years=YEAR_FILTERS, pars_id):
        self.rain_filters = rains
        self.montreal_filters = montreals
        self.year_filters = years
        self.first_trip_sent = False
        self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()
        self.id = pars_id

        self.channel.exchange_declare(exchange=STATIONS_EXCHANGE, exchange_type='fanout')
        self.channel.exchange_declare(exchange=WEATHER_EXCHANGE, exchange_type='fanout')

    def process_trip(self, trips):
        if not self.first_trip_sent:
            print("First Trip Announcement Sent")
            message = Message(FIRST_TRIP, self.id)
            bytes_message = message.create_message()
            self.channel.basic_publish(exchange=STATIONS_EXCHANGE, routing_key='', body=bytes_message,properties=pika.BasicProperties(delivery_mode=2))
            self.channel.basic_publish(exchange=WEATHER_EXCHANGE, routing_key='', body=bytes_message,properties=pika.BasicProperties(delivery_mode=2))
            self.first_trip_sent = True

        message = Message(trips, self.id)
        bytes_message = message.create_message()

        self.channel.basic_publish(exchange="", routing_key=RAIN_QUEUE, body=bytes_message,properties=pika.BasicProperties(delivery_mode=2))
        self.channel.basic_publish(exchange="", routing_key=MONTREAL_QUEUE, body=bytes_message,properties=pika.BasicProperties(delivery_mode=2))
        self.channel.basic_publish(exchange="", routing_key=YEAR_QUEUE, body=bytes_message,properties=pika.BasicProperties(delivery_mode=2))

    def process_station(self, stations):
        message = Message(stations, self.id)
        bytes_message = message.create_message()
        self.channel.basic_publish(exchange=STATIONS_EXCHANGE, routing_key='', body=bytes_message,properties=pika.BasicProperties(delivery_mode=2))

    def process_weather(self, weathers):
        message = Message(weathers, self.id)
        bytes_message = message.create_message()
        self.channel.basic_publish(exchange=WEATHER_EXCHANGE, routing_key='', body=bytes_message,properties=pika.BasicProperties(delivery_mode=2))

    def publish_stops(self):
        message = Message(STOP_TYPE, self.id)
        bytes_message = message.create_message()
        for _ in range(self.rain_filters):
            self.channel.basic_publish(exchange="", routing_key=RAIN_QUEUE, body=bytes_message,properties=pika.BasicProperties(delivery_mode=2))
        for _ in range(self.montreal_filters):
            self.channel.basic_publish(exchange="", routing_key=MONTREAL_QUEUE, body=bytes_message,properties=pika.BasicProperties(delivery_mode=2))
        for _ in range(self.year_filters):
            self.channel.basic_publish(exchange="", routing_key=YEAR_QUEUE, body=bytes_message,properties=pika.BasicProperties(delivery_mode=2))

    def add_data(self, body_read):
        ent_type, entity_to_process = read_message(body_read)

        if ent_type == TRIP_TYPE:
            self.process_trip(entity_to_process)
            return None
        elif ent_type == STATION_TYPE:
            self.process_station(entity_to_process)
            return None
        elif ent_type == WEATHER_TYPE:
            self.process_weather(entity_to_process)
            return None
        elif ent_type == STOP_TYPE:
            self.publish_stops()
            return STOP_TYPE
        else:
            raise Exception(f"Type Received Don't Make Sense {ent_type}")
