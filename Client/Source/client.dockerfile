FROM python:3.9.7-slim

WORKDIR /

COPY . /
COPY .../Common /Common

CMD /main.py
