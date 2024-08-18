#!/bin/bash

set -e

echo "Backup started"

echo "Backup pihole started"
docker exec -t pihole bash -c 'rm -rf /backup/*'
docker exec -t pihole bash -c 'cd /backup && pihole -a -t'
echo "Backup pihole finished"


echo "Backup gitea started"
docker exec -t gitea bash -c 'rm -rf /backup/*'
docker exec -t gitea bash -c 'sqlite3 /data/gitea/gitea.db ".backup /backup/gitea.db"'
echo "Backup gitea finished"


# echo "Backup calibre started"
# docker exec -t calibre-web bash -c 'rm -rf /backup/*'
# docker exec -t calibre-web bash -c 'sqlite3 /data/gitea/gitea.db ".backup /backup/gitea.db"'
# echo "Backup calibre finished"


echo "Backup postgres started"
docker exec -t postgres-db bash -c 'rm -rf /backup/*'
docker exec -t postgres-db bash -c 'pg_dumpall -U postgres > "/backup/postgres_dump.sql"'
echo "Backup postgres finished"


echo "Backup finished"

