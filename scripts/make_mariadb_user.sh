#!/bin/bash

set -e

# Скрипт для удобного создания пользователей и баз данных в контейнере mariadb для
# других приложений в контейнерах
#
# Использование:
#   - Добавить переменные окружения в файл ./.env по аналогии с существующими
#   - Заменить переменные NEW_USER, NEW_USER_PASSWORD, NEW_USER_DB в этом файле на
#     добавленные переменные
#   - Запустить скрипт, он создаст соответствующих пользователей

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source "$script_dir/../.env"

NEW_USER="$PG_PHOTOPRISM_USER"
NEW_USER_PASSWORD="$PG_PHOTOPRISM_PASSWORD"
NEW_USER_DB="$PG_PHOTOPRISM_DB"

# Просто, чтобы скрипт отпал, если есть проблемы с mariadb
docker exec -i mariadb mariadb -u root -p "${MARIADB_ROOT_PASSWORD}" -V

docker exec -i mariadb mariadb -u root -p"${MARIADB_ROOT_PASSWORD}" <<-EOSQL
    CREATE USER IF NOT EXISTS '${NEW_USER}'@'%' IDENTIFIED BY '${NEW_USER_PASSWORD}';
    CREATE DATABASE IF NOT EXISTS ${NEW_USER_DB};
    GRANT ALL ON ${NEW_USER_DB}.* TO '${NEW_USER}'@'%';
    SELECT User FROM mysql.user;
EOSQL

echo "Пользователь и БД созданы"

