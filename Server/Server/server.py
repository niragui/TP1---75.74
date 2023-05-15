import socket
import pika
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
        self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=DATA_QUEUE, durable=True)
        self.channel.queue_declare(queue=SERVER_QUEUE, durable=True)

        self.query = None
        self.querys_sent = 0
        self.sent_first_trip = False

    def run(self):
        client_socket, _ = self._server_socket.accept()
        self.__handle_client_connection(client_socket)
        self.publish_stops()

        self.wait_query(client_socket)

    def send_query(self, client_socket):
        message = ServerMessage(self.query)
        message.send_message(client_socket)

    def wait_query(self, client_socket):
        self.querys_sent = 0
        print("Waiting For Querys")

        def read_query(ch, method, properties, body):
            self.query = body.decode(ENCODING)
            print(f"Query Received {self.query}")
            self.send_query(client_socket)
            self.querys_sent += 1
            print(f"Querys Received: {self.querys_sent}")
            if self.querys_sent >= 3:
                self.channel.stop_consuming()
            else:
                print("A Seguir Esperando Querys")

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=SERVER_QUEUE, on_message_callback=read_query)

        self.channel.start_consuming()

    def publish_trip(self, lines):
        message = Message(TRIP_TYPE, lines, self.city)
        bytes_to_send = message.create_message()
        self.channel.basic_publish(exchange="",
                                    routing_key=DATA_QUEUE,
                                    body=bytes_to_send,
                                    properties=pika.BasicProperties(delivery_mode=2))

    def publish_station(self, lines):
        message = Message(STATION_TYPE, lines, self.city)
        bytes_to_send = message.create_message()
        self.channel.basic_publish(exchange="",
                                    routing_key=DATA_QUEUE,
                                    body=bytes_to_send,
                                    properties=pika.BasicProperties(delivery_mode=2))

    def publish_weather(self, lines):
        message = Message(WEATHER_TYPE, lines, self.city)
        bytes_to_send = message.create_message()
        self.channel.basic_publish(exchange="",
                                    routing_key=DATA_QUEUE,
                                    body=bytes_to_send,
                                    properties=pika.BasicProperties(delivery_mode=2))

    def publish_stops(self):
        for _ in range(self.parsers):
            message = Message(STOP_TYPE, "", self.city)
            bytes_to_send = message.create_message()
            self.channel.basic_publish(exchange="",
                                    routing_key=DATA_QUEUE,
                                    body=bytes_to_send,
                                    properties=pika.BasicProperties(delivery_mode=2))

    def __handle_client_connection(self, client_sock):
        while True:
            info_type, info = read_client_message(client_sock)
            if info_type == QUERY_CLIENT_TYPE:
                self.mode = QUERY_CLIENT_TYPE
                break
            elif info_type == CITY_CLIENT_TYPE:
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

    def __del__(self):
        self.is_awake = False
        self._server_socket.close()
