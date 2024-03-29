#!/usr/bin/env bash

/scripts/make_bareos_config.sh /etc_bareos /etc/bareos

# Run Dockerfile CMD
exec "$@"
