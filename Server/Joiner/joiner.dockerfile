FROM rabbitmq-python-base:0.0.1

COPY Server/Joiner /Joiner
COPY Server/InternalProtocol /InternalProtocol
CMD /Joiner/main.py