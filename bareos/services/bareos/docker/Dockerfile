FROM ubuntu:22.04 as bareos-base

ENV DEBIAN_FRONTEND noninteractive
ENV ADD_BAREOS_REPO_URL "https://download.bareos.org/current/xUbuntu_22.04/add_bareos_repositories.sh"
ENV ADD_BAREOS_REPO_PATH /tmp/add_bareos_repositories.sh

RUN apt-get update && \
  apt-get install -y curl \
                     gnupg \
                     vim-tiny \
                     tzdata

RUN curl -Ls $ADD_BAREOS_REPO_URL -o $ADD_BAREOS_REPO_PATH && \
  chmod +x $ADD_BAREOS_REPO_PATH && \
  bash $ADD_BAREOS_REPO_PATH
  

COPY make_bareos_config.sh /scripts/make_bareos_config.sh


# --------------- bareos-dir ---------------

FROM bareos-base as bareos-dir

RUN apt-get update && apt-get install -y bareos-database-postgresql \
                                         bareos-director \
                                         bareos-bconsole

EXPOSE 9101

COPY director-entrypoint.sh /scripts/director-entrypoint.sh
RUN chmod u+x /scripts/director-entrypoint.sh

ENTRYPOINT ["/scripts/director-entrypoint.sh"]

CMD ["/usr/sbin/bareos-dir", "-f"]


# --------------- bareos-webui ---------------

FROM bareos-base as bareos-webui

RUN apg-get update && apt-get install -y bareos-webui \
                                         nginx

EXPOSE 9100

COPY etc_nginx/default /etc/nginx/sites-enabled/default
COPY webui-entrypoint.sh /scripts/webui-entrypoint.sh
RUN chmod u+x /scripts/webui-entrypoint.sh

ENTRYPOINT ["/scripts/webui-entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]


# --------------- bareos-sd ---------------

FROM bareos-base as bareos-sd

RUN apt-get update && apt-get install -y bareos-storage

EXPOSE 9103

COPY sd-entrypoint.sh /scripts/sd-entrypoint.sh
RUN chmod u+x /scripts/sd-entrypoint.sh

ENTRYPOINT ["/scripts/sd-entrypoint.sh"]

CMD ["/usr/sbin/bareos-sd", "-f"]


# --------------- bareos-fd ---------------

FROM bareos-base as bareos-fd

RUN apt-get update && apt-get install -y bareos-filedaemon

EXPOSE 9102

COPY fd-entrypoint.sh /scripts/fd-entrypoint.sh
RUN chmod u+x /scripts/fd-entrypoint.sh

ENTRYPOINT ["/scripts/fd-entrypoint.sh"]

CMD ["/usr/sbin/bareos-fd", "-f"]

