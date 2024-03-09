# Удалить /etc/bareos
# Скопировать примонтированные конфиги в /etc/bareos
# Заменить переменные окружения

export PGHOST=${BAREOS__DB_HOST}
export PGUSER=${DB_ADMIN_USER}
export PGPASSWORD=${DB_ADMIN_PASSWORD}

[[ -z "${FORCE_DB_INIT}" ]] && FORCE_DB_INIT='false'

if [ ! -f /etc/bareos/bareos-db.control ] || [ "${FORCE_DB_INIT}" == 'true' ] ; then
  echo "Bareos DB init"
  echo "Bareos DB init: Create user ${BAREOS__DB_NAME}"
  psql -c "create user ${BAREOS__DB_NAME} with createdb createrole login;"
  echo "Bareos DB init: Set user password"
  psql -c "alter user ${BAREOS__DB_NAME} password '${BAREOS__DB_PASSWORD}';"

  /usr/lib/bareos/scripts/create_bareos_database
  /usr/lib/bareos/scripts/make_bareos_tables
  /usr/lib/bareos/scripts/grant_bareos_privileges

  # Control file
  touch /etc/bareos/bareos-db.control
fi

[[ -z "${DB_UPDATE}" ]] && DB_UPDATE='false'

if [ "${DB_UPDATE}" == 'true' ] ; then
  # Try Postgres upgrade
  echo "Bareoos DB update"
  echo "Bareoos DB update: Update tables"
  /usr/lib/bareos/scripts/update_bareos_tables
  echo "Bareoos DB update: Grant privileges"
  /usr/lib/bareos/scripts/grant_bareos_privileges
fi

# Run Dockerfile CMD
exec "$@"
