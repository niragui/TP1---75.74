import pika
from typing import List

from year_filter import YearFilter

from parserfilterprotocol import read_message, FIRST_TRIP, TRIP_TYPE, STATION_TYPE

from joinerprotocol import JoinerMessage

from constants import STOP_TYPE
from trip import Trip
from station import Station


WRITE_QUEUE = "year_joiner_queue"
TRIP_ANNOUNCE = 10000


class YearFilterWorker():
    def __init__(self, parsers):
        self.stations = {}
        self.trips_start_received = 0
        self.stops_received = 0
        self.parsers = parsers
        self.trips_filtered = 0

        self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()

    def send_value(self, value):
        message = JoinerMessage(value)
        bytes_to_send = message.create_message()
        self.channel.basic_publish(exchange='',
                                   routing_key=WRITE_QUEUE,
                                   body=bytes_to_send,
                                   properties=pika.BasicProperties(delivery_mode=2))

    def process_trips(self, trips: List[Trip]):
        values = []
        before = self.trips_filtered
        self.trips_filtered += len(trips)
        change = before%TRIP_ANNOUNCE - self.trips_filtered%TRIP_ANNOUNCE
        if change > 0:
            print(f"Trips Filtered: {self.trips_filtered}")

        for trip in trips:
            filter = YearFilter(trip, self.stations)
            value = filter.run()
            if value:
                values.append(value)

        if len(values) > 0:
            self.send_value(values)

        return value

    def process_stations(self, stations: List[Station]):
        for station in stations:
            station_id = station.get_id()
            self.stations.update({station_id: station})

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
        elif ent_type == STATION_TYPE:
            self.process_stations(entity)
        elif ent_type == STOP_TYPE:
            print("Stop Received")
            self.stops_received += 1
        elif ent_type == FIRST_TRIP:
            self.trips_start_received += 1
        else:
            raise Exception(f"Type Received Don't Make Sense {ent_type}")
