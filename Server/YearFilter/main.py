import pika
import time
import os

from year_filter_worker import YearFilterWorker

READ_TRIPS_QUEUE = "year_trips_queue"
STATIONS_EXCHANGE = "stations"

# Wait for rabbitmq to come up
time.sleep(10)

consumer_id = os.environ["FILTER_ID"]
parsers = int(os.environ["PARSERS"])
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))

channel = connection.channel()

channel.exchange_declare(exchange=STATIONS_EXCHANGE, exchange_type='fanout')

READ_DATA_QUEUE = channel.queue_declare(queue="", durable=True).method.queue
channel.queue_bind(READ_DATA_QUEUE, STATIONS_EXCHANGE)

channel.queue_declare(queue=READ_TRIPS_QUEUE, durable=True)

worker = YearFilterWorker(parsers)


def callback_data(ch, method, properties, body):
    worker.add_data(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    if worker.received_trip():
        print(f"{consumer_id} Has Finsihed Reading Stations")
        channel.stop_consuming()



def callback_trips(ch, method, properties, body):
    worker.add_data(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    if worker.received_stop():
        print(f"{consumer_id} Has Finsihed Its Work")
        worker.notify_stop()
        channel.stop_consuming()



channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue=READ_DATA_QUEUE, on_message_callback=callback_data)
channel.start_consuming()

channel.basic_consume(queue=READ_TRIPS_QUEUE, on_message_callback=callback_trips)
channel.start_consuming()

connection.close()
