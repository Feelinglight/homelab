#!/bin/bash

set -e

echo "Backup pihole started"

backup_path_in_docker="$1"

# docker exec -t pihole "cd ${backup_path_in_docker} && pihole -a -t"

echo "Backup pihole finished"

