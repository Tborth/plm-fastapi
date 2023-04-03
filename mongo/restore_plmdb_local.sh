
# sleep 5
# mongorestore --authenticationDatabase admin --db cargoeye-inventory --username user --password 'password' /home/dump

mongorestore --host localhost --port 27018 --authenticationDatabase admin --db cargoeye-inventory --username 'user' --password 'password' cge_plm_20220729_001002/cargoeye-inventory

#db_dumps/cge_plm_20220729_001002/cargoeye-inventory



