# Backup
docker exec postgres /usr/bin/mysqldump -u postgres --password=password ordina-pubquiz > backup.sql

# Restore
cat backup.sql | docker exec -i postgres /usr/bin/mysql -u postgres --password=root DATABASE