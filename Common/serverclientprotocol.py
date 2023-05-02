from socket import int_to_bytes, INT_LENGTH
from socket import read_int, read_socket, write_socket, send_int

import json


QUERY_CLIENT_TYPE = 0
CITY_CLIENT_TYPE = 1
STATION_CLIENT_TYPE = 2
WEATHER_CLIENT_TYPE = 3
TRIP_CLIENT_TYPE = 4
ENCODING = "utf-8"


class ClientMessage():
    def __init__(self, type, data):
        self.type = type
        self.data = data

    def create_message_city(self):
        bytes = b""
        type_byted = int_to_bytes(self.type)
        bytes += type_byted

        city_encoded = self.data.encode(ENCODING)
        length = len(city_encoded)

        length_byted = int_to_bytes(length)
        bytes += length_byted

        bytes += city_encoded
        return bytes

    def create_message_lines(self):
        bytes = b""
        type_byted = int_to_bytes(self.type)
        bytes += type_byted

        length = len(self.data)

        length_byted = int_to_bytes(length)
        bytes += length_byted

        for line in self.data:
            line_encoded = line.encode(ENCODING)
            length_line = len(line_encoded)
            length_byted = int_to_bytes(length_line)
            bytes += length_byted
            bytes += line_encoded

        return bytes

    def create_message_query(self):
        bytes = b""
        type_byted = int_to_bytes(self.type)
        bytes += type_byted

        return bytes

    def create_message(self):
        if self.type == CITY_CLIENT_TYPE:
            return self.create_message_city()
        elif self.type == QUERY_CLIENT_TYPE:
            return self.create_message_query()
        else:
            return self.create_message_lines()

    def send_message(self, socket):
        bytes_to_send = self.create_message()

        write_socket(socket, bytes_to_send)


def read_city(socket):
    message_length = read_int(socket)

    city = read_socket(socket, message_length)
    city = city.decode(ENCODING)

    return city


def read_lines(socket):
    amount = read_int(socket)

    lines = []

    for _ in range(0, amount):
        line_length = read_int(socket)
        line = read_socket(socket, line_length)
        line = line.decode(ENCODING)
        lines.append(line)

    return lines


def send_query(socket):
    send_int(socket, QUERY_CLIENT_TYPE)


def read_client_message(socket):
    message_type = read_int(socket)
    if message_type == QUERY_CLIENT_TYPE:
        return QUERY_CLIENT_TYPE, None
    elif message_type == CITY_CLIENT_TYPE:
        return CITY_CLIENT_TYPE, read_city()
    else:
        return message_type, read_lines()


class ServerMessage():
    def __init__(self, data) -> None:
        self.data = data

    def create_message(self):
        data = json.dumps(self.data)
        data = data.encode(ENCODING)

        length = len(data)
        length_bytes = int_to_bytes(length)

        bytes = b""
        bytes += length_bytes
        bytes += data

        return bytes

    def send_message(self, socket):
        bytes_to_send = self.create_message()

        write_socket(socket, bytes_to_send)


def read_query(socket):
    length_message = read_int(socket)
    data = read_socket(socket, length_message)

    return json.loads(data)
