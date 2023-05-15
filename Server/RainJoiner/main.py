import pika
import time
import os
import json

from rain_joiner_worker import RainJoinerWorker

READ_QUEUE = "rain_joiner_queue"
WRITE_QUEUE = "server_queue"

# Wait for rabbitmq to come up
time.sleep(10)

filters = int(os.environ["FILTER"])

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue=READ_QUEUE, durable=True)

worker = RainJoinerWorker(filters)


def callback(ch, method, properties, body):
    worker.add_trip(body)

    if worker.has_finished():
        print(f"Rain Joiner Has Finsihed Its Work")
        worker.send_query()
        print(f"Rain Joiner Has Sent The Query")
        channel.stop_consuming()

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=READ_QUEUE, on_message_callback=callback)

channel.start_consuming()
connection.close()
