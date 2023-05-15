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


class YearJoinerWorker():
    def __init__(self, filters):
        self.joiner = SumDictJoiner()
        self.filters = filters
        self.ends_found = 0
        self.time_ask = None
        self.names = {}

        self.channel = self.connection.channel()
        self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))

    def add_trip(self, body):
        data_type, data = read_message(body)

        if data_type == STOP_TYPE:
            self.ends_found += 1
            self.time_ask = time()
        else:
            for value in data:
                code = value[0]
                name = value[1]
                self.names.update({code: name})
                self.joiner.update((value[0], value[2]))

    def has_finished(self, total_filters):
        ends_found = self.ends_found >= total_filters
        before = self.time_ask
        if before is None:
            before = time()
        elapsed_time = time() - before

        return ends_found or elapsed_time >= TEN_MINUTES

    def get_parsed_values(self, values):
        aux = []

        for station, sum in values.items():
            if sum >= 0:
                name = self.names.get(station)
                aux.append(name)

        return aux

    def get_values(self):
        values = self.joiner.get_value()

        parsed_values = self.get_parsed_values(values)

        return {2: parsed_values}

    def send_query(self):
        value = self.send_values()

        bytes_to_send = json.dumps(value).encode(ENCODING)

        self.channel.basic_publish(exchange='',
                                   routing_key=SERVER_QUEUE,
                                   body=bytes_to_send,
                                   properties=pika.BasicProperties(delivery_mode=2))
