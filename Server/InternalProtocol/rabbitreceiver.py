
def error_method(message):
    raise Exception(f"Received {message} But No Method Associated")


class RabbitReceiver():
    def __init__(self, channel, queue_name=None, exchange=None) -> None:
        self.channel = channel
        if exchange:
            self.channel.exchange_declare(exchange=exchange,
                                          exchange_type='fanout')
            self.queue = self.channel.queue_declare(queue="", durable=True).method.queue
            self.channel.queue_bind(self.queue, exchange)
        elif queue_name:
            self.queue = queue_name
            self.channel.queue_declare(queue=queue_name, durable=True)
        else:
            raise Exception("You Must Receive Or From Queue Or From Exchange")

        self.user_method = error_method

    def callback(self, ch, method, properties, body):
        self.user_method(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def receive(self, receiver, prefetch=1):
        self.user_method = receiver
        self.channel.basic_qos(prefetch_count=prefetch)
        self.channel.basic_consume(queue=self.queue, on_message_callback=self.callback)
        self.channel.start_consuming()

    def close(self):
        if self.channel.is_open:
            self.channel.stop_consuming()