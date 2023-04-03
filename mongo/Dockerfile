FROM mongo:latest
WORKDIR /home
COPY ./cge_plm_20220729_001002/cargoeye-inventory/* /home/dump/
COPY ./restore_plmdb_local.sh /home/
# CMD chmod 777 /docker-entrypoint-initdb.d/import_data.sh /home/dump

# CMD mongod --fork --logpath /var/log/mongodb.log; \
#     mongorestore /home/dump/; \
#     mongod --shutdown; \
#     docker-entrypoint.sh mongod


# CMD  mongorestore --authenticationDatabase admin --db cargoeye-inventory1 --username user --password 'password' /home/dump