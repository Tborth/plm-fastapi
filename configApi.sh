#!/bin/bash
xhost +local:root
ENV_FILE=src/config/.env


echo "sourcing "$ENV_FILE
set -a
source $ENV_FILE

echo "Stopping configAPIs ..."
docker-compose down
docker-compose up -d --build 


docker exec -it cargoeye-plm_mongo_1 bash -c ./restore_plmdb_local.sh dump

echo "http://localhost:8001/"
# docker exec -it cargoeye-plm_mongo_1 bash

#mongorestore --authenticationDatabase admin --db cargoeye-inventory1 --username user --password 'password' /home/dump
#  --env-file $ENV_FILE
# docker-compose up
