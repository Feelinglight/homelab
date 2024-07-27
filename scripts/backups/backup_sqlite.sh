#!/bin/bash

set -e

echo "Backup sqlite3 started"

db_path="$1"
backup_db_path="$2"

# sqlite3 "${db_path}" ".backup ${backup_db_path}"

echo "Backup sqlite3 finished"

