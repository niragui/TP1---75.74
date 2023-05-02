FROM python:3.9.7-slim

RUN pip install --upgrade pip
RUN pip3 install pika
RUN pip3 install haversine

COPY ./Server/Server /
COPY ./Server/InternalProtocol /
COPY ./Common /Common

CMD ["python3", "main.py"]