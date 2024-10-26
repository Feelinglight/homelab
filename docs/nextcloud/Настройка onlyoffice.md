# Настройка onlyoffice

Onlyoffice запускается в отдельном контейнере. В
[официальном образе](https://hub.docker.com/r/onlyoffice/documentserver)
БД и rabbitmq для onlyoffice запускаются в самом контейнере onlyoffice.

Несмотря на то, что страницы onlyoffice открываются на домене nextcloud,
onlyoffice все равно должен быть виден клиенту nextcloud.

Настройки onlyoffice в nextcloud должны быть такие:

- **Адрес ONLYOFFICE Docs**: адрес onlyoffice, который доступен для клиента
- **Секретный ключ**: значение переменной окружения ``JWT_SECRET`` контейнера onlyoffice
- **Адрес ONLYOFFICE Docs для внутренних запросов сервера**: адрес onlyoffice в сети контйнеров
  (обычно это имя контейнера в docker compose)
- **Адрес сервера для внутренних запросов ONLYOFFICE Docs**: адрес nextcloud в сети контейнеров

Для traefik нужно также
[настроить http-заголовки](https://forum.onlyoffice.com/t/adding-documentserver-to-existing-traefik-proxy-works-halfway-but-cannot-open-documents/3239/12).

В trusted_domains nextcloud должно быть добавлено доменное имя, по которому onlyoffice обращается
к nextcloud (имя контейнера в docker compose)

