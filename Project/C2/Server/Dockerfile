FROM python:3.9.1-slim-buster

COPY ./routes routes
COPY ./requirements.txt requirements.txt
COPY ./database database
COPY ./app.py app.py
COPY ./cert.pem cert.pem
COPY ./key.pem key.pem

RUN pip3 install -r ./requirements.txt
EXPOSE 5000

CMD flask run --host=0.0.0.0 --port=5000 --cert=cert.pem --key=key.pem