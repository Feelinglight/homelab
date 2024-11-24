#!/bin/bash

set -e

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
services_dir="$script_dir/../services"

echo "Backup started"

echo "Backup pihole started"
docker exec -t pihole bash -c 'rm -rf /backup/*'
docker exec -t pihole bash -c 'cd /backup && pihole -a -t'
echo "Backup pihole finished"


echo "Backup gitea started"
docker exec -t gitea bash -c 'rm -rf /backup/*'
docker exec -t gitea bash -c 'sqlite3 /data/gitea/gitea.db ".backup /backup/gitea.db"'
echo "Backup gitea finished"


echo "Backup calibre started"
rm -rf "${services_dir}/calibre-web/backup/*"
sqlite3 "${services_dir}/calibre-web/data/app.db" ".backup ${services_dir}/calibre-web/backup/app.db"
sqlite3 "${services_dir}/calibre-web/data/gdrive.db" ".backup ${services_dir}/calibre-web/backup/gdrive.db"
sqlite3 "${services_dir}/calibre-web/data/metadata.db" ".backup ${services_dir}/calibre-web/backup/metadata.db"
echo "Backup calibre finished"


echo "Backup postgres started"
docker exec -t postgres-db bash -c 'rm -rf /backup/*'
docker exec -t postgres-db bash -c 'pg_dumpall -U postgres > "/backup/postgres_dump.sql"'
echo "Backup postgres finished"


echo "Backup mariadb started"
docker exec -t mariadb bash -c 'rm -rf /backup/*'
docker exec -t mariadb bash -c 'mariadb-dump --user=root --password="${MARIADB_ROOT_PASSWORD}" --all-databases > "/backup/mariadb_dump.sql"'
echo "Backup mariadb finished"


echo "Backup finished"

