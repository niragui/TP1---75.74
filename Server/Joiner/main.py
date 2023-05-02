import pika
import time
import os
import json


from joiner_worker import JoinerWorker
from constants import FILTERS_AMOUNT
from joinerserverprotocol import QUERY_TYPE, ENCODING

READ_QUEUE = "joiner_queue"
WRITE_QUEUE = "server_queue"

# Wait for rabbitmq to come up
time.sleep(10)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue=READ_QUEUE, durable=True)
channel.queue_declare(queue=WRITE_QUEUE, durable=True)

worker = JoinerWorker()
query_asked = False


def send_values():
    values = worker.get_values()
    bytes_to_send = json.dumps(values).decode(ENCODING)
    channel.basic_publish(exchange='', routing_key=WRITE_QUEUE,
                          body=bytes_to_send,
                          properties=pika.BasicProperties(delivery_mode=2))


def callback(ch, method, properties, body):
    data_type = worker.add_trip(body)
    if worker.has_finished(FILTERS_AMOUNT):
        send_values()
        channel.stop_consuming()

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=READ_QUEUE, on_message_callback=callback)

channel.start_consuming()
connection.close()
