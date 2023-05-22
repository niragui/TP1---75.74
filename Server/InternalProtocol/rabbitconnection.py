import pika
from rabbitreceiver import RabbitReceiver
from rabbitsender import RabbitSender


class RabbitConnection():
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))

        self.channel = self.connection.channel()

    def create_queue_receiver(self, queue_name=None, exchange=None):
        return RabbitReceiver(self.channel, queue_name=queue_name,
                              exchange=exchange)

    def create_queue_sender(self, queue_name=None, exchange=None):
        return RabbitSender(self.channel, queue_name=queue_name,
                            exchange=exchange)

    def close(self):
        if self.channel.is_open:
            self.channel.close()
        if self.connection.is_open:
            self.connection.close()

