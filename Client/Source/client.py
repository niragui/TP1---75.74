import socket
import os
import time

from serverclientprotocol import TRIP_CLIENT_TYPE, STATION_CLIENT_TYPE, WEATHER_CLIENT_TYPE, CITY_CLIENT_TYPE, QUERY_CLIENT_TYPE
from serverclientprotocol import ClientMessage, send_query, read_query

ENCODING = "utf-8"
BATCH_AMOUNT = 100

TOTAL_QUERIES = 3

CITIES = ["Montreal", "Toronto", "Washington"]
FILES = {}
FILES.update({STATION_CLIENT_TYPE: "stations.csv"})
FILES.update({TRIP_CLIENT_TYPE: "trips.csv"})
FILES.update({WEATHER_CLIENT_TYPE: "weather.csv"})


def count_time(start_time, end_time):
    seconds = round(end_time - start_time, 2)
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


class Client():
    def __init__(self, server_ip, port) -> None:
        self.server_ip = server_ip
        self.port = port
        self.socket = None
        self.query = None

    def run(self):
        start = time.time()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_ip, self.port))
        self.send_values(STATION_CLIENT_TYPE)
        self.send_values(WEATHER_CLIENT_TYPE)
        self.send_values(TRIP_CLIENT_TYPE)
        self.ask_reply()
        self.print_queries()
        self.socket.close()
        end = time.time()
        time_elapsed = count_time(start, end)
        print(f"Time Taken: {time_elapsed}")


    def get_file(self, city, data_type):
        directory = city.lower()
        file_name = FILES.get(data_type)

        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            f = open(file_path, "r", encoding=ENCODING)
            f.readline()  # Skip Header
            return f
        else:
            return None

    def get_lines(self, file):
        lines = []

        for _ in range(BATCH_AMOUNT):
            line = file.readline()
            if line:
                lines.append(line)

        return lines

    def send_values(self, data_type):
        for city in CITIES:
            message = ClientMessage(CITY_CLIENT_TYPE, city)
            message.send_message(self.socket)
            file = self.get_file(city, data_type)
            if file is None:
                continue
            lines = self.get_lines(file)
            while True:
                if len(lines) > 0:
                    message = ClientMessage(data_type, lines)
                    message.send_message(self.socket)
                if len(lines) < BATCH_AMOUNT:
                    break
                else:
                    lines = self.get_lines(file)
            file.close()

    def ask_reply(self):
        send_query(self.socket)

    def print_queries(self):
        queries_read = 0
        print("Waiting For Querys")
        while queries_read < TOTAL_QUERIES:
            query = read_query(self.socket)
            queries_read += 1
            print(query)

    def __del__(self):
        if self.socket:
            self.socket.close()