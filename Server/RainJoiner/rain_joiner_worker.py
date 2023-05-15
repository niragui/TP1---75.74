import json
import pika

from time import time

from average_joiner import AverageJoiner

from joinerprotocol import read_message
from joinerserverprotocol import ENCODING
from constants import STOP_TYPE

TEN_MINUTES = 60 * 10
SERVER_QUEUE = "server_queue"


class RainJoinerWorker():
    def __init__(self, filters):
        self.joiner = AverageJoiner()
        self.filters = filters
        self.ends_found = 0
        self.time_ask = None

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
            for value in data:
                self.joiner.update(value)

    def has_finished(self):
        ends_found = self.ends_found >= self.filters
        before = self.time_ask
        if before is None:
            before = time()
        elapsed_time = time() - before

        return ends_found or elapsed_time >= TEN_MINUTES

    def get_values(self):
        value = self.joiner.get_value()

        return {1: value}

    def send_query(self):
        value = self.get_values()

        bytes_to_send = json.dumps(value).encode(ENCODING)

        self.channel.basic_publish(exchange='',
                                   routing_key=SERVER_QUEUE,
                                   body=bytes_to_send,
                                   properties=pika.BasicProperties(delivery_mode=2))


