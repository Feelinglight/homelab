#!/bin/bash

# docker build --no-cache -t bar-dir --target bareos-dir .
docker build -t bar-dir --target bareos-dir .
docker build -t bar-web --target bareos-webui .
docker build -t bar-sd --target bareos-sd .
docker build -t bar-fd --target bareos-fd .

docker rmi $(docker images --filter "dangling=true" -q --no-trunc)

