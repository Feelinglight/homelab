#!/usr/bin/env bash

set -e

if [ $# -lt 2 ]; then
    echo 'Error: bareos configs folders are not specified'
    exit 1
fi

template_configs_folder="$1"
bareos_configs_folder="$2"

rm -rf "$bareos_configs_folder"/*
cp -r "$template_configs_folder/"* "$bareos_configs_folder"

find "$bareos_configs_folder" -type f | while read -r file; do
    # echo "File $file:"
    # for var in $(printenv | grep '^BAREOS__'); do
    for var_name in "${!BAREOS__@}"; do
        var_value="$(printenv $var_name)"

        # echo "sed -i "s/{{$var_name}}/$var_value/g" "$file""
        # Каракули после var_value для правильного экранирования слэшей
        sed -i "s/{{$var_name}}/${var_value//\//\\/}/g" "$file"
    done
done

