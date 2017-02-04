# launch all
docker-compose up -d rabbitmq server client

# scale up clients
docker-compose scale client=10

# check state
docker-compose ps
docker-compose logs -f client server
