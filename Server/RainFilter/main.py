import pika
import time
import os

from rain_filter_worker import RainFilterWorker

READ_TRIPS_QUEUE = "rain_trips_queue"
WEATHERS_EXCHANGE = "weathers"

# Wait for rabbitmq to come up
time.sleep(20)

consumer_id = os.environ["FILTER_ID"]
parsers = int(os.environ["PARSERS"])
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))

channel = connection.channel()

channel.exchange_declare(exchange=WEATHERS_EXCHANGE, exchange_type='fanout')

READ_DATA_QUEUE = channel.queue_declare(queue="", durable=True).method.queue
channel.queue_bind(READ_DATA_QUEUE, WEATHERS_EXCHANGE)

channel.queue_declare(queue=READ_TRIPS_QUEUE, durable=True)

worker = RainFilterWorker(parsers)


def callback_data(ch, method, properties, body):
    worker.add_data(body)

    if worker.received_trip():
        channel.stop_consuming()

    ch.basic_ack(delivery_tag=method.delivery_tag)


def callback_trips(ch, method, properties, body):
    worker.add_data(body)

    if worker.received_stop():
        worker.notify_stop()
        channel.stop_consuming()

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue=READ_DATA_QUEUE, on_message_callback=callback_data)
channel.start_consuming()

channel.basic_consume(queue=READ_TRIPS_QUEUE, on_message_callback=callback_trips)
channel.start_consuming()

connection.close()
