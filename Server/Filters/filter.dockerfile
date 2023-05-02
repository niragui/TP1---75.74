FROM rabbitmq-python-base:0.0.1

COPY Server/Filters /Filters
COPY Server/InternalProtocol /InternalProtocol
CMD /Filters/main.py