#!/bin/bash

set -e

echo "Backup started"

backup_path="$1"
docker exec -t postgres pg_dumpall -U postgres > "$backup_path"

echo "Backup finished"

