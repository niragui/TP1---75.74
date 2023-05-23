from typing import List

from rain_filter import RainFilter

from parserfilterprotocol import read_message, FIRST_TRIP, TRIP_TYPE, WEATHER_TYPE
from rabbitconnection import RabbitConnection
from joinerprotocol import JoinerMessage

from constants import STOP_TYPE
from trip import Trip
from weather import Weather


WRITE_QUEUE = "rain_joiner_queue"
TRIP_ANNOUNCE = 1000000

READ_TRIPS_QUEUE = "rain_trips_queue"
WEATHER_EXCHANGE = "weathers"


class RainFilterWorker():
    def __init__(self, parsers):
        self.weathers = {}
        self.trips_start_received = 0
        self.stops_received = []
        self.parsers = parsers
        self.trips_filtered = 0
        self.connection = RabbitConnection()

        self.joiner_queue = self.connection.create_queue_sender(queue_name=WRITE_QUEUE)
        self.stop_queue = self.connection.create_queue_sender(queue_name=READ_TRIPS_QUEUE)
        self.trips_queue = self.connection.create_queue_receiver(queue_name=READ_TRIPS_QUEUE)
        self.weathers_queue = self.connection.create_queue_receiver(exchange=WEATHER_EXCHANGE)

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
        return len(self.stops_received) >= self.parsers

    def notify_stop(self):
        message = JoinerMessage(STOP_TYPE)
        bytes_to_send = message.create_message()
        self.joiner_queue.send(bytes_to_send)

    def process_stop(self, sender, bytes_read):
        if sender in self.stops_received:
            self.stop_queue.send(bytes_read)
        else:
            print(f"Received Stop From {sender}")
            self.stops_received.append(sender)

    def add_data(self, body_read):
        ent_type, entity = read_message(body_read)

        if ent_type == TRIP_TYPE:
            self.process_trips(entity)
        elif ent_type == WEATHER_TYPE:
            self.process_weathers(entity)
        elif ent_type == STOP_TYPE:
            self.process_stop(entity, body_read)
            if self.received_stop():
                print("Finished Reading Trips")
                self.trips_queue.close()
                self.notify_stop()
        elif ent_type == FIRST_TRIP:
            self.trips_start_received += 1
            if self.received_trip():
                print("Finished Reading Stations")
                self.weathers_queue.close()
        else:
            raise Exception(f"Type Received Don't Make Sense {ent_type}")

    def run(self):
        self.weathers_queue.receive(self.add_data)
        self.trips_queue.receive(self.add_data)
        self.connection.close()

    def stop(self):
        self.connection.close()
