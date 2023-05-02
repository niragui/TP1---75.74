FROM python:3.9

WORKDIR /

COPY /requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /Server/Server/main.py /main.py
CMD /main.py