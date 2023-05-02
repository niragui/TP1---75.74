import pika
import time
import os
import json


from joiner_worker import JoinerWorker
from constants import FILTERS_AMOUNT
from joinerserverprotocol import QUERY_TYPE, ENCODING

READ_QUEUE = "joiner_queue"
WRITE_QUEUE = "server_queue"
TEN_MINUTES = 60 * 10

# Wait for rabbitmq to come up
time.sleep(10)

consumer_id = os.environ["CONSUMER_ID"]
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
    data_type = worker.add_data(body)
    if data_type == QUERY_TYPE:
        query_asked = True
        start_time = time.time()
    if query_asked:
        if worker.has_finished(FILTERS_AMOUNT):
            send_values()
            channel.stop_consuming()
        elapsed_time = time.time() - start_time
        if elapsed_time >= TEN_MINUTES:
            print("Ten Minutes Have Passed, assuming one filter broke down")

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=READ_QUEUE, on_message_callback=callback)

channel.start_consuming()
connection.close()
