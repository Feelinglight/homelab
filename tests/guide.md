# Роутер

- На роутере присвоить адрес dns серверу pihole
- Настроить роутер безопаснее (пароли wifi и админки)

# Сервер

Настроить статический ip и DNS (он не должен входить в пул динамических адресов dhcp сервера)

Отключить suspend:

- Работает: https://askubuntu.com/questions/15520/how-can-i-tell-ubuntu-to-do-nothing-when-i-close-my-laptop-lid
- Не пробовал: https://askubuntu.com/questions/473037/how-to-permanently-disable-sleep-suspend

# pihole

- Как найти сервисы, которые используют 53 порт:

  sudo lsof -i -P -n | grep LISTEN | grep 53

- Убить systemd-resolve

  systemctl disable systemd-resolved.service
  systemctl stop systemd-resolved

- Как зайти в веб pihole

  localhost/admin

- Как сбросить пароль:

  google: pihole default password ???


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

