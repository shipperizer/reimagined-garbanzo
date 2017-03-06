# launch all
docker-compose up -d rabbitmq redis server client beat

# scale up clients
docker-compose scale client=15

# check state
docker-compose ps
docker-compose logs -f client server
