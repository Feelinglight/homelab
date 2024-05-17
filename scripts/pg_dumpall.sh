#!/bin/bash

set -e

echo "Backup postgres started"

container_name="$1"
backup_path="$2"
docker exec -t "$container_name" pg_dumpall -U postgres > "$backup_path"

echo "Backup postgres finished"

