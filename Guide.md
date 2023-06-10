# Подготовка виртуалки

На чистой виртуалке Ubuntu 22.04:

```bash
sudo apt update
sudo pat full-upgrade
sudo apt install -y openssh-server
ip a
sudo reboot
```

На основном хосте:

```sh
python3 -m pip install ansible
ansible-galaxy install gantsign.oh-my-zsh
```

```bash
ssh-copy-id -i ~/.ssh/id_ed25519 homelab@192.168.122.143
```


## Gitea

На клиенте:

Настроить gitea.local на ip адрес хоста

На хосте:

**/home/homelab/docker-compose.yaml**

```yml
version: "2"

services:
  gitea:
    container_name: gitea
    image: gitea/gitea:1.19.3-rootless
    restart: always
    volumes:
      - ./gitea/data:/var/lib/gitea
      - ./gitea/config:/etc/gitea
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    ports:
      - "80:80"
```

**/usr/local/bin/gitea-shell**

```sh
#!/bin/sh
/usr/bin/docker exec -i --env SSH_ORIGINAL_COMMAND="$SSH_ORIGINAL_COMMAND" gitea sh "$@"
```

**/etc/ssh/ssh_config.d/gitea.conf**:

```sh
Match User git
  AuthorizedKeysCommandUser git
  AuthorizedKeysCommand /usr/bin/docker exec -i gitea /usr/local/bin/gitea keys -c /etc/gitea/app.ini -e git -u %u -t %t -k %k
```

```ini
APP_NAME = Homelab Git Server
RUN_USER = git
RUN_MODE = prod

[repository]
ROOT = /var/lib/gitea/git/repositories

[repository.local]
LOCAL_COPY_PATH = /tmp/gitea/local-repo

[repository.upload]
TEMP_PATH = /tmp/gitea/uploads

[server]
APP_DATA_PATH           = /var/lib/gitea
SSH_DOMAIN              = gitea
HTTP_PORT               = 443
ROOT_URL                = http://gitea
DISABLE_SSH             = false
; In rootless gitea container only internal ssh server is supported
START_SSH_SERVER        = true
SSH_PORT                = 22
SSH_LISTEN_PORT         = 2222
BUILTIN_SSH_SERVER_USER = git
LFS_START_SERVER        = true
DOMAIN                  = gitea
LFS_JWT_SECRET          = _SUHxvpNPGnpjv5pekgKP-1-ZzkxlHCO1cceLUIUMao
OFFLINE_MODE            = false

[database]
PATH     = /var/lib/gitea/data/gitea.db
DB_TYPE  = sqlite3
HOST     = localhost:3306
NAME     = gitea
USER     = root
PASSWD   =
SCHEMA   =
SSL_MODE = disable
CHARSET  = utf8
LOG_SQL  = false

[session]
PROVIDER_CONFIG = /var/lib/gitea/data/sessions
PROVIDER        = file

[picture]
AVATAR_UPLOAD_PATH            = /var/lib/gitea/data/avatars
REPOSITORY_AVATAR_UPLOAD_PATH = /var/lib/gitea/data/repo-avatars

[attachment]
PATH = /var/lib/gitea/data/attachments

[log]
ROOT_PATH = /var/lib/gitea/data/log
MODE      = console
LEVEL     = info
ROUTER    = console

[security]
INSTALL_LOCK                  = true
SECRET_KEY                    =
REVERSE_PROXY_LIMIT           = 1
REVERSE_PROXY_TRUSTED_PROXIES = *
INTERNAL_TOKEN                = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYmYiOjE2ODYzMjg4MTN9.90KRly75XuKNHqG3LGcjjUl_Ihge4D4gzwZcam8ov_I
PASSWORD_HASH_ALGO            = pbkdf2

[service]
DISABLE_REGISTRATION              = false
REQUIRE_SIGNIN_VIEW               = false
REGISTER_EMAIL_CONFIRM            = false
ENABLE_NOTIFY_MAIL                = false
ALLOW_ONLY_EXTERNAL_REGISTRATION  = false
ENABLE_CAPTCHA                    = false
DEFAULT_KEEP_EMAIL_PRIVATE        = false
DEFAULT_ALLOW_CREATE_ORGANIZATION = true
DEFAULT_ENABLE_TIMETRACKING       = true
NO_REPLY_ADDRESS                  = noreply.localhost

[lfs]
PATH = /var/lib/gitea/git/lfs

[mailer]
ENABLED = false

[openid]
ENABLE_OPENID_SIGNIN = true
ENABLE_OPENID_SIGNUP = true

[cron.update_checker]
ENABLED = false

[repository.pull-request]
DEFAULT_MERGE_STYLE = merge

[repository.signing]
DEFAULT_TRUST_MODEL = committer
```

```sh
touch /home/homelab/services/docker-compose.yaml
mkdir -p /home/homelab/services/gitea/{data,config}
sudo chown 1000:1000 /home/homelab/services/gitea/config/ /home/homelab/services/gitea/data/

sudo adduser git
# Права на docker exec (gitea-shell)
sudo usermod -a -G docker git

sudo chmod +x /usr/local/bin/gitea-shell
sudo usermod -s /usr/local/bin/gitea-shell git

sudo systemctl restart sshd
```
