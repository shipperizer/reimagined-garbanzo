.PHONY: client server build client beat

server:
	python server.py

registrator:
	python server.py registrator

client:
	python client.py

build:
	pip install -r requirements.txt

beat:
	rm -f /run/celerybeat.pid
	celery -A client beat --pidfile=/run/celerybeat.pid --schedule=/run/celerybeat-schedule

build:
	pip install -r requirements.txt
