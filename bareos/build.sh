# docker build -t bar-dir ./director
# docker build -t bar-sd ./storage
# docker build -t bar-web ./webui
# docker build -t bar-fd ./client

docker build -t bar-dir --target bareos-dir .
docker build -t bar-sd --target bareos-sd .
docker build -t bar-web --target bareos-webui .
docker build -t bar-fd --target bareos-fd .

