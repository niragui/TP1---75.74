FROM rabbitmq-python-base:0.0.1

COPY /Server/Server /Server
COPY /Server/InternalProtocol /InternalProtocol
COPY /Common /Common

CMD /Server.main.py