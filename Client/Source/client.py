import socket
import os

from serverclientprotocol import TRIP_CLIENT_TYPE, STATION_CLIENT_TYPE, WEATHER_CLIENT_TYPE, CITY_CLIENT_TYPE, QUERY_CLIENT_TYPE
from serverclientprotocol import ClientMessage, send_query, read_query

ENCODING = "utf-8"
BATCH_AMOUNT = 10

CITIES = ["Montreal", "Toronto", "Washington"]
FILES = {}
FILES.update({STATION_CLIENT_TYPE: "stations.csv"})
FILES.update({TRIP_CLIENT_TYPE: "trips.csv"})
FILES.update({WEATHER_CLIENT_TYPE: "weather.csv"})


class Client():
    def __init__(self, server_ip, port) -> None:
        self.server_ip = server_ip
        self.port = port
        self.socket = None
        self.query = None

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_ip, self.port))
        self.send_values(STATION_CLIENT_TYPE)
        self.send_values(WEATHER_CLIENT_TYPE)
        self.send_values(TRIP_CLIENT_TYPE)
        self.ask_reply()
        self.print_query()

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
        self.query = read_query(self.socket)

    def print_query(self):
        query_one = self.query.get(1)
        print(f"Average On Rainy Days: {query_one}")

        query_two = self.query.get(2)
        print("Stations that duplicated their trips in 2017:")
        for station in query_two:
            print(f"\t{station}")

        query_three = self.query.get(3)
        print("Montreal Stations that have an above 6km average to reach:")
        for station in query_three:
            print(f"\t{station}")
