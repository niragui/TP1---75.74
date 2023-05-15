import pika
from typing import List


from rain_filter import RainFilter

from parserfilterprotocol import read_message, FIRST_TRIP, TRIP_TYPE, WEATHER_TYPE

from joinerprotocol import JoinerMessage

from constants import STOP_TYPE
from trip import Trip
from weather import Weather


WRITE_QUEUE = "rain_joiner_queue"


class RainFilterWorker():
    def __init__(self, parsers):
        self.weathers = {}
        self.trips_start_received = 0
        self.stops_received = 0
        self.parsers = parsers

        self.channel = self.connection.channel()
        self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))

    def send_value(self, value):
        message = JoinerMessage(value)
        bytes_to_send = message.create_message()
        self.channel.basic_publish(exchange='',
                                   routing_key=WRITE_QUEUE,
                                   body=bytes_to_send,
                                   properties=pika.BasicProperties(delivery_mode=2))

    def process_trips(self, trips: List[Trip]):
        values = []

        for trip in trips:
            filter = RainFilter(trip, self.weathers)
            value = filter.run()
            if value:
                values.append(value)

        if len(values) > 0:
            self.send_value(values)

        return value

    def process_weathers(self, weathers: List[Weather]):
        for weather in weathers:
            weather_id = weather.get_id()
            self.weathers.update({weather_id: weather})

    def received_trip(self):
        return self.trips_start_received >= self.parsers

    def received_stop(self):
        return self.stops_received >= self.parsers

    def notify_stop(self):
        message = JoinerMessage(STOP_TYPE)
        bytes_to_send = message.create_message()
        self.channel.basic_publish(exchange='',
                                   routing_key=WRITE_QUEUE,
                                   body=bytes_to_send,
                                   properties=pika.BasicProperties(delivery_mode=2))


    def add_data(self, body_read):
        ent_type, entity = read_message(body_read)

        if ent_type == TRIP_TYPE:
            self.process_trips(entity)
        elif ent_type == WEATHER_TYPE:
            self.process_weathers(entity)
        elif ent_type == STOP_TYPE:
            self.stops_received += 1
        elif ent_type == FIRST_TRIP:
            self.trips_start_received += 1
        else:
            raise Exception(f"Type Received Don't Make Sense {ent_type}")
