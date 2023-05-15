import pika
import time
import os

from parser import Parser
from constants import STOP_TYPE

DATA_QUEUE = "data_queue"

# Wait for rabbitmq to come up
time.sleep(10)

consumer_id = os.environ["PARSER_ID"]
rains = int(os.environ["RAIN"])
montreals = int(os.environ["MONTREAL"])
years = int(os.environ["YEAR"])
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))

channel = connection.channel()
channel.queue_declare(queue=DATA_QUEUE, durable=True)

parser = Parser(rains, montreals, years)


def callback_data(ch, method, properties, body):
    value = parser.add_data(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    if value is STOP_TYPE:
        print(f"{consumer_id} Has Finsihed Its Work")
        channel.stop_consuming()



channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=DATA_QUEUE, on_message_callback=callback_data)

channel.start_consuming()
connection.close()
