import pika
import sys
import random
import time

# Wait for rabbitmq to come up
time.sleep(10)

# Create RabbitMQ communication channel
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

FILTER_QUEUE = "task_queue"
WRITE_QUEUE = "server_queue"


channel.queue_declare(queue=FILTER_QUEUE, durable=True)

channel.basic_publish()


connection.close()