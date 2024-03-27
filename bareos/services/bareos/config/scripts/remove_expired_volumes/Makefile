
download_bareos_json:
	docker exec bareos-dir bash -c 'echo -e ".api 2\nllist job=DockerLinuxJob" | bconsole' > ./scripts/data/jobs.json; \
	sed -i '1,16d' ./scripts/data/jobs.json; \
	docker exec bareos-dir bash -c 'echo -e ".api 2\nllist jobmedia job=DockerLinuxJob" | bconsole' > ./scripts/data/jobmedia.json; \
	sed -i '1,16d' ./scripts/data/jobmedia.json; \


run_from_console: download_bareos_json
	PYTHONPATH="PYTHONPATH:${PWD}" python3 ./scripts/run_from_console.py


run_from_bareos:
	PYTHONPATH="PYTHONPATH:${PWD}" python3 -m src -l Full -j DockerLinuxJob -s DockerLinuxStorage -d

