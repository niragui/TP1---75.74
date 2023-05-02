FROM python:3.9.7-slim

RUN pip install --upgrade pip
RUN pip3 install pika

COPY ./Server/Server ./Server
COPY ./Server/InternalProtocol ./InternalProtocol
COPY ./Common /Common

CMD ["python3", "Server/main.py"]