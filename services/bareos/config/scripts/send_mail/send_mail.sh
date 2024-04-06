#!/bin/bash

python3 ./send_mail.py \
  --smtp-address 'smtp.yandex.ru' \
  --smtp-port 587 \
  --smtp-login 'login' \
  --smtp-password 'password' \
  --from 'Bareos <login@mail.ru>' \
  --recipients 'rec@mail.ru' \
  --subject 'subject' \
  --email-text "$(cat <<EOF
<h2>%t %e</h2>
<p>
  <a href='http://homelab:9100/job/details/%i'>Job: %n (%i)</a><br>
  Job unique name: %j<br>
  Job level: %l<br>
  Client: %c (%h)<br>
  Time: %s<br>
</p>
EOF
)"

