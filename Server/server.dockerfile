FROM python:3.9

COPY /requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /Server/Server /Server
COPY /Server/InternalProtocol /InternalProtocol
COPY /Common /Common

CMD /Server.main.py