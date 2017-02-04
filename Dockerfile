FROM python:3.6-slim

RUN apt-get clean && apt-get update && apt-get -y install build-essential

COPY Makefile requirements.txt /var/app/

WORKDIR /var/app

RUN make build

COPY . /var/app

CMD ["make", "server"]
