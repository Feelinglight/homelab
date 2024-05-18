#!/bin/bash

# Старый вариант Mail Command, не используется потому что так невозможно отправить логи на почту

#  Mail Command = "python3 /usr/local/bin/send_mail/send_mail.py "
#                   "--smtp-address '{{BAREOS__SMTP_ADDRESS}}' "
#                   "--smtp-port '{{BAREOS__SMTP_PORT}}' "
#                   "--smtp-login '{{BAREOS__SMTP_LOGIN}}' "
#                   "--smtp-password '{{BAREOS__SMTP_PASSWORD}}' "
#                   "--from '{{BAREOS__SMTP_FROM}}' "
#                   "--recipients '{{BAREOS__SMTP_TO}}' "
#                   "--subject 'Bareos: %t %e of %c %l' "
#                   "--email-text \"<h2>%t %e</h2>"
#                                 "<p>"
#                                   "<a href='http://{{BAREOS__OUTER_ADDRESS}}/job/details/%i\'><b>Job</b>: %n (%i)</a><br>"
#                                   "<b>Job unique name</b>: %j<br>"
#                                   "<b>Job level</b>: %l<br>"
#                                   "<b>Client</b>: %c (%h)<br>"
#                                   "<b>Time</b>: %s<br>"
#                                 "</p>\""

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

