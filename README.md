# Подготовка виртуалки

На чистой виртуалке Ubuntu 22.04:

```bash
sudo apt update
sudo pat full-upgrade
sudo apt install -y openssh-server
ip a
sudo reboot
```

# Подготовка основного хоста

```sh
sudo apt install -y python3-pip avahi-daemon

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


```sh
touch /home/homelab/services/docker-compose.yaml
mkdir -p /home/homelab/services/gitea/{data,config}
sudo chown 1000:1000 /home/homelab/services/gitea/config/ /home/homelab/services/gitea/data/

sudo adduser git
# Права на docker exec
sudo usermod -a -G docker git

sudo chmod +x /usr/local/bin/gitea-shell
sudo usermod -s /usr/local/bin/gitea-shell git

sudo systemctl restart sshd
```
