FROM python:3.9

WORKDIR /

COPY /requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /Server/Filters /Filters
COPY /Server/InternalProtocol /InternalProtocol
CMD /Filters/main.py