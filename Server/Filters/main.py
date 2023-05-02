import pika
import time
import os

from filter_worker import FilterWorker
from joinerprotocol import JoinerMessage
from constants import STOP_TYPE

READ_TRIPS_QUEUE = "task_queue"
WRITE_QUEUE = "joiner_queue"

# Wait for rabbitmq to come up
time.sleep(10)

consumer_id = os.environ["FILTER_ID"]
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))

channel = connection.channel()
READ_DATA_QUEUE = channel.queue_declare(queue="", durable=True).method.queue
channel.queue_bind(READ_DATA_QUEUE, "notification_exchange")
channel.queue_declare(queue=READ_TRIPS_QUEUE, durable=True)
channel.queue_declare(queue=WRITE_QUEUE, durable=True)

worker = FilterWorker()


def send_value(value):
    message = JoinerMessage(value[0], value[1])
    bytes_to_send = message.create_message()
    channel.basic_publish(exchange='', routing_key=WRITE_QUEUE,
                          body=bytes_to_send,
                          properties=pika.BasicProperties(delivery_mode=2))


def callback_data(ch, method, properties, body):
    worker.add_data(body)

    if worker.received_trip():
        channel.stop_consuming()

    ch.basic_ack(delivery_tag=method.delivery_tag)


def callback_trips(ch, method, properties, body):
    values = worker.add_data(body)

    if values is not None:
        for value in values:
            send_value(value)
            if value[0] == STOP_TYPE:
                print(f"{consumer_id} Has Finsihed Its Work")
                channel.stop_consuming()

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=READ_DATA_QUEUE, on_message_callback=callback_data)
channel.basic_consume(queue=READ_TRIPS_QUEUE, on_message_callback=callback_trips)

channel.start_consuming()
connection.close()
