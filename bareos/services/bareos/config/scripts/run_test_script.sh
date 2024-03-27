 docker exec bareos-dir bash -c 'echo -e ".api 2\nllist job=DockerLinuxJob" | bconsole' > ./jobs.json
 docker exec bareos-dir bash -c 'echo -e ".api 2\nllist jobmedia job=DockerLinuxJob" | bconsole' > ./jobmedia.json

