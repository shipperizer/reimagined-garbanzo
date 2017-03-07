FROM python:3.6-slim

RUN apt-get clean && apt-get update && apt-get -y install build-essential supervisor

COPY Makefile client.conf server.conf beat.conf requirements.txt /var/app/

WORKDIR /var/app

RUN make build

COPY *.py /var/app/

CMD ["bash"]
