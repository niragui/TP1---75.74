import socket

from rabbitconnection import RabbitConnection
from serverparserprotocol import Message, TRIP_TYPE, STATION_TYPE, WEATHER_TYPE, STOP_TYPE
from joinerserverprotocol import ENCODING
from serverclientprotocol import read_client_message, QUERY_CLIENT_TYPE, ServerMessage
from serverclientprotocol import CITY_CLIENT_TYPE, WEATHER_CLIENT_TYPE, TRIP_CLIENT_TYPE, STATION_CLIENT_TYPE

DATA_QUEUE = "data_queue"
SERVER_QUEUE = "server_queue"


class Server:
    def __init__(self, port, parsers):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen()
        self.parsers = parsers
        self.is_awake = True
        self.city = None
        self.mode = None

        self.connection = RabbitConnection()

        self.data_queue = self.connection.create_queue_sender(queue_name=DATA_QUEUE)
        self.server_queue = self.connection.create_queue_receiver(queue_name=SERVER_QUEUE)

        self.query = None
        self.querys_sent = 0
        self.sent_first_trip = False
        self.client_socket = None

    def run(self):
        self.client_socket, _ = self._server_socket.accept()
        print("Client Accepted")
        self.__handle_client_connection()
        self.publish_stops()

        self.wait_query()

    def send_query(self):
        message = ServerMessage(self.query)
        message.send_message(self.client_socket)

    def read_query(self, body):
        self.query = body.decode(ENCODING)
        print(f"Query Received {self.query}")
        self.send_query()
        self.querys_sent += 1
        if self.querys_sent >= 3:
            self.server_queue.close()

    def wait_query(self):
        self.querys_sent = 0
        print("Waiting For Querys")

        self.server_queue.receive(self.read_query)

    def publish_trip(self, lines):
        message = Message(TRIP_TYPE, lines, self.city)
        bytes_to_send = message.create_message()
        self.data_queue.send(bytes_to_send)

    def publish_station(self, lines):
        message = Message(STATION_TYPE, lines, self.city)
        bytes_to_send = message.create_message()
        self.data_queue.send(bytes_to_send)

    def publish_weather(self, lines):
        message = Message(WEATHER_TYPE, lines, self.city)
        bytes_to_send = message.create_message()
        self.data_queue.send(bytes_to_send)

    def publish_stops(self):
        for _ in range(self.parsers):
            message = Message(STOP_TYPE, "", self.city)
            bytes_to_send = message.create_message()
            self.data_queue.send(bytes_to_send)

    def __handle_client_connection(self):
        while True:
            info_type, info = read_client_message(self.client_socket)
            if info_type == QUERY_CLIENT_TYPE:
                self.mode = QUERY_CLIENT_TYPE
                break
            elif info_type == CITY_CLIENT_TYPE:
                print(f"Server Registro Ciudad: {info}")
                self.city = info
            elif info_type == TRIP_CLIENT_TYPE:
                self.publish_trip(info)
            elif info_type == STATION_CLIENT_TYPE:
                self.publish_station(info)
            elif info_type == WEATHER_CLIENT_TYPE:
                self.publish_weather(info)

        if self.mode != QUERY_CLIENT_TYPE:
            raise Exception("Exit Loop Before Query Were Requested")

    def exit_gracefully(self):
        self.__del__()

    def stop(self):
        self.is_awake = False
        self._server_socket.close()
        if self.client_socket:
            self.client_socket.close()
        self.connection.close()

    def __del__(self):
        self.stop()
