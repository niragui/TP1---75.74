import json
import pika

from time import time
from threading import Timer

from average_dict_joiner import AverageDictJoiner
from rabbitconnection import RabbitConnection

from joinerprotocol import read_message
from joinerserverprotocol import ENCODING
from constants import STOP_TYPE

TEN_MINUTES = 60 * 10
SERVER_QUEUE = "server_queue"
SYNC_WAIT = 60
READ_QUEUE = "rain_joiner_queue"

TRIP_ANNOUNCE = 500000


class RainJoinerWorker():
    def __init__(self, filters):
        self.joiner = AverageDictJoiner()
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

    def get_values(self):
        value = self.joiner.get_value()

        return {1: value}

    def send_query(self):
        value = self.get_values()

        bytes_to_send = json.dumps(value).encode(ENCODING)

        self.query_queue.send(bytes_to_send)

    def __del__(self):
        self.trips_queue.close()

    def run(self):
        self.trips_queue.receive(self.handle_message)
        self.trips_queue.close()
        self.send_query()
