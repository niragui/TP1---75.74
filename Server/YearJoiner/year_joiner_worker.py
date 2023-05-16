import json
import pika

from time import time

from sum_dict_joiner import SumDictJoiner

from joinerprotocol import read_message
from constants import STOP_TYPE
from joinerserverprotocol import ENCODING

MIN_QUERY_MONTERAL = 6000
TEN_MINUTES = 60 * 10
SERVER_QUEUE = "server_queue"

TRIP_ANNOUNCE = 500000


class YearJoinerWorker():
    def __init__(self, filters):
        self.joiner = SumDictJoiner()
        self.filters = filters
        self.ends_found = 0
        self.time_ask = None
        self.trips_joined = 0
        self.stopper = None

        self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()

    def add_trip(self, body):
        data_type, data = read_message(body)

        if data_type == STOP_TYPE:
            print("Stop Received")
            self.ends_found += 1
            self.time_ask = time()
        else:
            before = self.trips_joined
            self.trips_joined += len(data)
            change = before % TRIP_ANNOUNCE - self.trips_joined % TRIP_ANNOUNCE
            if change > 0:
                print(f"Trips Joined: {self.trips_joined}")

            for value in data:
                self.joiner.update(value)

    def has_finished(self):
        ends_found = self.ends_found >= self.filters
        before = self.time_ask
        if before is None:
            before = time()
        elapsed_time = time() - before

        return ends_found or elapsed_time >= TEN_MINUTES

    def received_stop(self):
        return self.ends_found > 0

    def start_stopper(self, stopper):
        self.stopper = stopper
        self.stopper.start()

    def cancel_stopper(self):
        if self.stopper:
            self.stopper.cancel()
            self.stopper = None

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

        self.channel.basic_publish(exchange='',
                                   routing_key=SERVER_QUEUE,
                                   body=bytes_to_send,
                                   properties=pika.BasicProperties(delivery_mode=2))

    def __del__(self):
        self.cancel_stopper()
