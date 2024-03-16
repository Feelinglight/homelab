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

COPY make_bareos_config.sh /make_bareos_config.sh


# --------------- bareos-dir ---------------

FROM bareos-base as bareos-dir

RUN apt-get install -y bareos-database-postgresql \
                       bareos-director \
                       bareos-bconsole

EXPOSE 9101

COPY director-entrypoint.sh /director-entrypoint.sh
RUN chmod u+x /director-entrypoint.sh

ENTRYPOINT ["/director-entrypoint.sh"]

# CMD ["/usr/sbin/bareos-dir", "-u", "bareos", "-f"]
CMD ["/usr/sbin/bareos-dir", "-f"]


# --------------- bareos-webui ---------------

FROM bareos-base as bareos-webui

RUN apt-get install -y bareos-webui \
                       nginx

EXPOSE 80

COPY webui-entrypoint.sh /webui-entrypoint.sh
RUN chmod u+x /webui-entrypoint.sh

ENTRYPOINT ["/webui-entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]


# --------------- bareos-sd ---------------

FROM bareos-base as bareos-sd

RUN apt-get install -y bareos-storage

EXPOSE 9103

COPY sd-entrypoint.sh /sd-entrypoint.sh
RUN chmod u+x /sd-entrypoint.sh

ENTRYPOINT ["/sd-entrypoint.sh"]

CMD ["/usr/sbin/bareos-sd", "-f"]


# --------------- bareos-fd ---------------

FROM bareos-base as bareos-fd

RUN apt-get install -y bareos-filedaemon

EXPOSE 9102

COPY fd-entrypoint.sh /fd-entrypoint.sh
RUN chmod u+x /fd-entrypoint.sh

ENTRYPOINT ["/fd-entrypoint.sh"]

CMD ["/usr/sbin/bareos-fd", "-f"]

