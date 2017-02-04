.PHONY: client server build

server:
	python server.py registrator >> .logs &
	python server.py >> .logs &
	tail -f .logs

registrator:
	python server.py registrator

client:
	python client.py

build:
	pip install -r requirements.txt
