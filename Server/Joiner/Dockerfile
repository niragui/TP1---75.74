FROM python:3.9

RUN pip install --upgrade pip
RUN pip3 install pika

COPY ./Server/Joiner /Joiner
COPY ./Server/InternalProtocol /InternalProtocol

CMD ["python3", "./main.py"]
