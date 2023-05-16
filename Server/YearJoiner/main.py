import pika
import time
import os
import json
from threading import Timer

from year_joiner_worker import YearJoinerWorker

READ_QUEUE = "year_joiner_queue"
WRITE_QUEUE = "server_queue"
SYNC_WAIT = 60

# Wait for rabbitmq to come up
time.sleep(10)

filters = int(os.environ["FILTER"])

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue=READ_QUEUE, durable=True)

worker = YearJoinerWorker(filters)
stop_timer = None


def callback(ch, method, properties, body):
    worker.add_trip(body)

    if stop_timer is None and worker.received_stop():
        stop_timer = Timer(SYNC_WAIT, channel.start_consuming)
        stop_timer.start()
    ch.basic_ack(delivery_tag=method.delivery_tag)

    if worker.has_finished():
        print(f"Year Joiner Has Finsihed Its Work")
        worker.send_query()
        print(f"Year Joiner Has Sent The Query")
        stop_timer.cancel()
        channel.stop_consuming()

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=READ_QUEUE, on_message_callback=callback)

channel.start_consuming()
connection.close()
