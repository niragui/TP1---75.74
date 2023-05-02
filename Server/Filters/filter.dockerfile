FROM python:3.9.7-slim

RUN pip install --upgrade pip
RUN pip3 install pika

COPY Server/Filers /Filters
COPY Server/InternalProtocol /InternalProtocol

CMD ["python3", "./main.py"]
