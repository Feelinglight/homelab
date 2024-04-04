#!/bin/bash

# NOCACHE="--no-cache"
NOCACHE=
BAREOS_VERSION="23.0.3"

docker build ${NOCACHE} -t feelinglight/bareos-dir:${BAREOS_VERSION} -t feelinglight/bareos-dir:latest --target bareos-dir .
docker build ${NOCACHE} -t feelinglight/bareos-webui:${BAREOS_VERSION} -t feelinglight/bareos-webui:latest --target bareos-webui .
docker build ${NOCACHE} -t feelinglight/bareos-fd:${BAREOS_VERSION} -t feelinglight/bareos-fd:latest --target bareos-fd .
docker build ${NOCACHE} -t feelinglight/bareos-sd:${BAREOS_VERSION} -t feelinglight/bareos-sd:latest --target bareos-sd .

docker rmi $(docker images --filter "dangling=true" -q --no-trunc)


docker push feelinglight/bareos-dir:${BAREOS_VERSION}
docker push feelinglight/bareos-dir:latest

docker push feelinglight/bareos-sd:${BAREOS_VERSION}
docker push feelinglight/bareos-sd:latest

docker push feelinglight/bareos-fd:${BAREOS_VERSION}
docker push feelinglight/bareos-fd:latest

docker push feelinglight/bareos-webui:${BAREOS_VERSION}
docker push feelinglight/bareos-webui:latest

