# launch all
docker-compose up -d rabbitmq server client

# scale up clients
docker-compose scale client=6

# check state
docker-compose ps
