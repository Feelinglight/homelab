# Роутер

- На роутере присвоить адрес dns серверу pihole.
- Настроить роутер безопаснее (пароли wifi и админки)

# Сервер

Настроить статический ip

Отключить suspend:

- Работает: https://askubuntu.com/questions/15520/how-can-i-tell-ubuntu-to-do-nothing-when-i-close-my-laptop-lid
- Не пробовал: https://askubuntu.com/questions/473037/how-to-permanently-disable-sleep-suspend

# Сервер и все клиенты

- Включить Cache=no-negative в /etc/systemd/resolved.conf, чтобы избежать глюков с локальными доменами pi-hole
- Потом sudo systemctl restart systemd-resolved.service

# pihole

- Как найти сервисы, которые используют 53 порт:

  sudo lsof -i -P -n | grep LISTEN | grep 53

- Убить systemd-resolve

  systemctl disable systemd-resolved.service
  systemctl stop systemd-resolved

  Вместо ссылки в /etc/resolv.conf создать файл, в нем прописать 2 адреса dns:

  nameserver 127.0.0.1 (pihole)
  nameserver 8.8.8.8 (на случай если pihole будет лежать)

- Как зайти в веб pihole

  localhost/admin

  На /admin автоматически не перенаправляет!!!


- *.home.local должны отправлять на хост traefik

# gitea

- Создать пользователя git на хосте где докер
- Настроить gitea из фронтенда
- Настроить проброс ssh методом **SSH Shell with AuthorizedKeysCommand**


# samba

- Настроить шару, чтобы в нее нельзя было получить доступ без пароля
- Сбилдить образ из **other/smb-docker* (предварительно настроить **smb.conf**
- Добавить в образ докера wsdd для автоматического обнаружения шары в винде


# nextcloud

- Добавить в контейнер ``apt-get update && apt-get install -y procps smbclient`` для samba
- Разрешить подключения из внутренней сети:

  В контейнере в **/var/www/html/config/config.php (примерно):

  ```bash
  'trusted_domains' => 
  array (
    0 => 'localhost:8080',
    1 => '192.168.5.*',
    2 => '192.168.5.*:8080',
  ),
  ```


[Подключить smb-шару](https://docs.nextcloud.com/server/latest/admin_manual/configuration_files/external_storage/smb.html):

- Добавить приложение ncloud external storages
- Добавить samba шару в настройках ncloud

> На всякий случай:
>
> Перезапуск nextcloud в контейнере: ``/etc/init.d/apache2 restart``

