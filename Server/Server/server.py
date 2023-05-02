import socket
import pika
from constants import FILTERS_AMOUNT
from serverfilterprotocol import Message, TRIP_TYPE, STATION_TYPE, WEATHER_TYPE, STOP_TYPE
from joinerprotocol import JoinerMessage
from joinerserverprotocol import QUERY_TYPE, ENCODING
from serverclientprotocol import read_client_message, QUERY_CLIENT_TYPE, ServerMessage
from serverclientprotocol import CITY_CLIENT_TYPE, WEATHER_CLIENT_TYPE, TRIP_CLIENT_TYPE, STATION_CLIENT_TYPE

FILTER_QUEUE = "task_queue"
JOINER_QUEUE = "joiner_queue"
SERVER_QUEUE = "server_queue"


class Server:
    def __init__(self, port):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen()
        self.is_awake = True
        self.city = None
        self.mode = None
        self.connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()
        self.notification = 'notification_exchange'

        self.channel.exchange_declare(exchange=self.notification,
                                      exchange_type='fanout')


        self.channel.queue_declare(queue=FILTER_QUEUE, durable=True)
        self.channel.queue_bind(queue=FILTER_QUEUE, exchange=self.notification)
        self.channel.queue_declare(queue=JOINER_QUEUE, durable=True)
        self.channel.queue_declare(queue=SERVER_QUEUE, durable=True)

        self.query = None

    def run(self):
        client_socket, _ = self._server_socket.accept()
        self.__handle_client_connection(client_socket)
        self.publish_stops()

        self.ask_query()
        self.wait_query()
        self.send_query(client_socket)

    def send_query(self, client_socket):
        message = ServerMessage(self.query)
        message.send_message(client_socket)

    def wait_query(self):
        def read_query(ch, method, properties, body):
            self.query = body.decode(ENCODING)
            self.channel.stop_consuming()
        self.channel.basic_consume(queue=SERVER_QUEUE, on_message_callback=read_query)

    def ask_query(self):
        message = JoinerMessage(QUERY_TYPE, [])
        bytes_to_send = message.create_message()
        self.channel.basic_publish(exchange='',
                                   routing_key=JOINER_QUEUE,
                                   body=bytes_to_send,
                                   properties=pika.BasicProperties(delivery_mode=2))

    def publish_trip(self, lines):
        for line in lines:
            message = Message(TRIP_TYPE, line, self.city)
            bytes_to_send = message.create_message()
            self.channel.basic_publish(exchange='',
                                       routing_key=FILTER_QUEUE,
                                       body=bytes_to_send,
                                       properties=pika.BasicProperties(delivery_mode=2))

    def publish_station(self, lines):
        for line in lines:
            message = Message(STATION_TYPE, line, self.city)
            bytes_to_send = message.create_message()
            self.channel.basic_publish(exchange=self.notification,
                                       routing_key=FILTER_QUEUE,
                                       body=bytes_to_send,
                                       properties=pika.BasicProperties(delivery_mode=2))

    def publish_weather(self, lines):
        for line in lines:
            message = Message(WEATHER_TYPE, line, self.city)
            bytes_to_send = message.create_message()
            self.channel.basic_publish(exchange=self.notification,
                                       routing_key=FILTER_QUEUE,
                                       body=bytes_to_send,
                                       properties=pika.BasicProperties(delivery_mode=2))

    def publish_stops(self):
        message = Message(STOP_TYPE, [], self.city)
        bytes_to_send = message.create_message()
        self.channel.basic_publish(exchange=self.notification,
                                   routing_key=FILTER_QUEUE,
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
