FROM python:3.9.7-slim
COPY Client/Source /
COPY Common /Common

CMD /main.py
