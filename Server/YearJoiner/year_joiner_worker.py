import json
import pika

from time import time
from threading import Timer

from sum_dict_joiner import SumDictJoiner
from rabbitconnection import RabbitConnection

from joinerprotocol import read_message
from constants import STOP_TYPE
from joinerserverprotocol import ENCODING

MIN_QUERY_MONTERAL = 6000
TEN_MINUTES = 60 * 10
SERVER_QUEUE = "server_queue"
SYNC_WAIT = 60
READ_QUEUE = "year_joiner_queue"

TRIP_ANNOUNCE = 500000


class YearJoinerWorker():
    def __init__(self, filters):
        self.joiner = SumDictJoiner()
        self.filters = filters
        self.ends_found = 0
        self.time_ask = None
        self.trips_joined = 0
        self.stopper = None

        self.connection = RabbitConnection()

        self.trips_queue = self.connection.create_queue_receiver(queue_name=READ_QUEUE)
        self.query_queue = self.connection.create_queue_sender(queue_name=SERVER_QUEUE)

    def handle_trip(self, trips):
        before = self.trips_joined
        self.trips_joined += len(trips)
        change = before % TRIP_ANNOUNCE - self.trips_joined % TRIP_ANNOUNCE
        if change > 0:
            print(f"Trips Joined: {self.trips_joined}")

        for value in trips:
            self.joiner.update(value)

    def handle_stop(self):
        print("Stop Received")
        if self.ends_found == 0:
            self.stopper = Timer(SYNC_WAIT, self.trips_queue.close)
            self.stopper.start()
        self.ends_found += 1
        self.time_ask = time()
        if self.has_finished():
            self.trips_queue.close()
            self.stopper.cancel()

    def handle_message(self, body):
        data_type, data = read_message(body)

        if data_type == STOP_TYPE:
            self.handle_stop()
        else:
            self.handle_trip(data)

    def has_finished(self):
        return self.ends_found >= self.filters

    def get_parsed_values(self, values):
        aux = []

        print(values)

        for station, sum in values.items():
            if sum >= 0:
                aux.append(station)

        return aux

    def get_values(self):
        values = self.joiner.get_value()

        parsed_values = self.get_parsed_values(values)

        return {2: parsed_values}

    def send_query(self):
        value = self.get_values()

        bytes_to_send = json.dumps(value).encode(ENCODING)

        self.query_queue.send(bytes_to_send)

    def __del__(self):
        self.connection.close()

    def run(self):
        self.trips_queue.receive(self.handle_message)
        self.trips_queue.close()
        self.send_query()
        self.connection.close()

    def stop(self):
        self.connection.close()
