#!/usr/bin/env bash

set -e

if [[ $# -eq 0 ]] ; then
    echo 'Error: bareos configs folder is not specified'
    exit 1
fi

bareos_configs_folder="$1"

rm -rf /etc/bareos/*
cp -r "$bareos_configs_folder/." /etc/bareos

find /etc/bareos -type f | while read -r file; do
    echo "File $file:"
    for var in $(printenv | grep "^BAREOS__"); do
        var_name=$(echo "$var" | cut -d= -f1)
        var_value=$(echo "$var" | cut -d= -f2-)
        sed -i "s/{{$var_name}}/$var_value/g" "$file"
    done
done

