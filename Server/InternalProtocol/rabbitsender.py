import pika

DELIVERY_TWO = pika.BasicProperties(delivery_mode=2)


class RabbitSender():
    def __init__(self, channel, queue_name=None, exchange=None) -> None:
        self.channel = channel
        if exchange:
            self.is_exchange = True
            self.exchange = exchange
            self.channel.exchange_declare(exchange=exchange,
                                          exchange_type='fanout')
        elif queue_name:
            self.is_exchange = False
            self.queue = queue_name
        else:
            raise Exception("You Must Send On Queue Or On Exchange")

    def send_exchange(self, body):
        if not self.is_exchange:
            raise Exception("Not A Exchange Queue")
        self.channel.basic_publish(exchange=self.exchange, routing_key='',
                                   body=body,
                                   properties=DELIVERY_TWO)

    def send_queue(self, body):
        if self.is_exchange:
            raise Exception("Not A Work Queue")
        self.channel.basic_publish(exchange="", routing_key=self.queue,
                                   body=body,
                                   properties=DELIVERY_TWO)

    def send(self, body):
        if self.is_exchange:
            self.send_exchange(body)
        else:
            self.send_queue(body)
