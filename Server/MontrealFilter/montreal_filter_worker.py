from typing import List

from montreal_filter import MontrealFilter

from parserfilterprotocol import read_message, FIRST_TRIP, TRIP_TYPE, STATION_TYPE
from rabbitconnection import RabbitConnection
from joinerprotocol import JoinerMessage

from constants import STOP_TYPE
from trip import Trip
from station import Station


WRITE_QUEUE = "montreal_joiner_queue"
TRIP_ANNOUNCE = 1000000

READ_TRIPS_QUEUE = "montreal_trips_queue"
STATIONS_EXCHANGE = "stations"


class MontrealFilterWorker():
    def __init__(self, parsers):
        self.stations = {}
        self.trips_start_received = 0
        self.stops_received = []
        self.trips_filtered = 0
        self.parsers = parsers

        self.connection = RabbitConnection()

        self.joiner_queue = self.connection.create_queue_sender(queue_name=WRITE_QUEUE)
        self.stop_queue = self.connection.create_queue_sender(queue_name=READ_TRIPS_QUEUE)
        self.trips_queue = self.connection.create_queue_receiver(queue_name=READ_TRIPS_QUEUE)
        self.stations_queue = self.connection.create_queue_receiver(exchange=STATIONS_EXCHANGE)

    def send_value(self, value):
        message = JoinerMessage(value)
        bytes_to_send = message.create_message()
        self.joiner_queue.send(bytes_to_send)

    def process_trips(self, trips: List[Trip]):
        values = []
        before = self.trips_filtered
        self.trips_filtered += len(trips)
        change = before % TRIP_ANNOUNCE - self.trips_filtered % TRIP_ANNOUNCE
        if change > 0:
            print(f"Trips Filtered: {self.trips_filtered}")

        for trip in trips:
            filter = MontrealFilter(trip, self.stations)
            value = filter.run()
            if value:
                values.append(value)

        if len(values) > 0:
            self.send_value(values)

        return value

    def process_stop(self, sender, bytes_read):
        if sender in self.stops_received:
            self.stop_queue.send(bytes_read)
        else:
            print(f"Received Stop From {sender}")
            self.stops_received.append(sender)

    def process_stations(self, stations: List[Station]):
        for station in stations:
            station_id = station.get_id()
            self.stations.update({station_id: station})

    def received_trip(self):
        return self.trips_start_received >= self.parsers

    def received_stop(self):
        return len(self.stops_received) >= self.parsers

    def notify_stop(self):
        message = JoinerMessage(STOP_TYPE)
        bytes_to_send = message.create_message()
        self.joiner_queue.send(bytes_to_send)

    def add_data(self, body_read):
        ent_type, entity = read_message(body_read)

        if ent_type == TRIP_TYPE:
            self.process_trips(entity)
        elif ent_type == STATION_TYPE:
            self.process_stations(entity)
        elif ent_type == STOP_TYPE:
            self.process_stop(entity, body_read)
            if self.received_stop():
                print("Finished Reading Trips")
                self.trips_queue.close()
                self.notify_stop()
        elif ent_type == FIRST_TRIP:
            self.trips_start_received += 1
            print(f"First Trip! Received: {self.trips_start_received}")
            if self.received_trip():
                print("Finished Reading Stations")
                self.stations_queue.close()
        else:
            raise Exception(f"Type Received Don't Make Sense {ent_type}")

    def run(self):
        self.stations_queue.receive(self.add_data)
        self.trips_queue.receive(self.add_data)
        self.connection.close()

    def stop(self):
        self.connection.close()
