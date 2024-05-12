#!/bin/bash

set -e

# Скрипт для удобного создания пользователей и баз данных в контейнере postgres для
# других приложений в контейнерах
#
# Использование:
#   - Добавить переменные окружения в файл ./.env по аналогии с существующими
#   - Заменить переменные NEW_USER, NEW_USER_PASSWORD, NEW_USER_DB в этом файле на
#     добавленные переменные
#   - Запустить скрипт, он создаст соответствующих пользователей

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source "$script_dir/../.env"

NEW_USER="$PG_GITEA_USER"
NEW_USER_PASSWORD="$PG_GITEA_PASSWORD"
NEW_USER_DB="$PG_GITEA_DB"

# Просто, чтобы скрипт отпал, если есть проблемы с postgres
docker exec -i postgres psql -U postgres -V

docker exec -i postgres psql -U postgres <<-EOSQL
    CREATE USER $NEW_USER WITH PASSWORD '$NEW_USER_PASSWORD';
    CREATE DATABASE $NEW_USER_DB;
    GRANT ALL PRIVILEGES ON DATABASE $NEW_USER_DB TO $NEW_USER;
    ALTER DATABASE $NEW_USER_DB OWNER TO $NEW_USER;
EOSQL

