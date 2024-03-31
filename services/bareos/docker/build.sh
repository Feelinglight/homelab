#!/bin/bash

# NOCACHE="--no-cache"
NOCACHE=

docker build ${NOCACHE} -t bareos-dir --target bareos-dir .
docker build ${NOCACHE} -t bareos-web --target bareos-webui .
docker build ${NOCACHE} -t bareos-sd --target bareos-sd .
docker build ${NOCACHE} -t bareos-fd --target bareos-fd .

docker rmi $(docker images --filter "dangling=true" -q --no-trunc)

