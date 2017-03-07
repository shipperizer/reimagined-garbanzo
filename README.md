# reimagined-garbanzo

## Architecture

Creating a publish-subscribe architecture

* one central server sends a limited amount of message (10000) to all clients
* chance to send messages on demand from server to all clients
* clients log received messages and also feedback on their status thru a celery beat task
* redis is used as local broker for the clients and the server (one is enough in this case, although each client app is supposed to have it's own local broker, servers can have a single common one)
* rabbitmq is the mean of transport


## Useful commands

Send message on-demand from server to client:

```
docker-compose exec server celery -A server call server.data
```
