#!/usr/bin/env bash

/make_bareos_config.sh /etc_bareos /etc/bareos-webui

php-fpm8.1

# Run Dockerfile CMD
exec "$@"
