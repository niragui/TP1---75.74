FROM python:3.9.7-slim

WORKDIR /

COPY Client/Source /
COPY Common /Common

CMD /main.py
