# Подготовка

На ВМ:

```bash
sudo apt install -y openssh-server
ip a
```

На основном хосте:

```bash
ssh-copy-id ubuntu@domain_or_ip
```

# Установка

ansible-playbook main.yml -i hosts

