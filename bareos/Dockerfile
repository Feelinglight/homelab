FROM ubuntu:22.04 as bareos-base

ENV DEBIAN_FRONTEND noninteractive
ENV ADD_BAREOS_REPO_URL "https://download.bareos.org/current/xUbuntu_22.04/add_bareos_repositories.sh"
ENV ADD_BAREOS_REPO_PATH /tmp/add_bareos_repositories.sh

RUN apt-get update && \
  apt-get install -y curl \
                     gnupg \
                     vim-tiny

RUN curl -Ls $ADD_BAREOS_REPO_URL -o $ADD_BAREOS_REPO_PATH && \
  chmod +x $ADD_BAREOS_REPO_PATH && \
  bash $ADD_BAREOS_REPO_PATH && \
  apt-get update


# --------------- bareos-dir ---------------

FROM bareos-base as bareos-dir

RUN apt-get install -y bareos-database-postgresql \
                       bareos-director \
                       bareos-bconsole

EXPOSE 9101

# CMD ["/usr/sbin/bareos-dir", "-u", "bareos", "-f"]
CMD ["/usr/sbin/bareos-dir", "-f"]


# --------------- bareos-sd ---------------

FROM bareos-base as bareos-sd

RUN apt-get install -y bareos-storage

EXPOSE 9103

CMD ["/usr/sbin/bareos-sd", "-f"]


# --------------- bareos-webui ---------------

FROM bareos-base as bareos-webui

RUN apt-get install -y bareos-webui

EXPOSE 80

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]


# --------------- bareos-fd ---------------

FROM bareos-base as bareos-fd

RUN apt-get install -y bareos-filedaemon

EXPOSE 9102

CMD ["/usr/sbin/bareos-fd", "-f"]

