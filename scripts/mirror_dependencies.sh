#!/bin/bash

set -e

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source "$script_dir/../.env"


################################################################################
# Загружает произвольный файл по http и заливает его в gitea packages
# Arguments:
#   $1: Адрес загружаемого файла
#   $2: Имя пакета gitea
#   $3: Версия пакета gitea
################################################################################
upload_file_as_package() {
  remote_address="$1"
  package_name="$2"
  version="$3"

  gitea_package_address="https://$GITEA_DOMAIN/api/packages/main/generic/$package_name/$version/"

  tmp_folder=/tmp/temp
  mkdir -p "$tmp_folder"
  tmp_file="$tmp_folder/$package_name"
  curl "$remote_address" -o "$tmp_file"

  curl --user "$GITEA_LOGIN:$GITEA_PACKAGES_API_TOKEN" --upload-file "$tmp_file" "$gitea_package_address"

  rm -rf $tmp_folder
}

# ------------------------------ docker images ------------------------------

docker login "$GITEA_DOMAIN"

docker_images=(
  "juanluisbaptiste/postfix:1.7.1"
  "feelinglight/bareos-dir:23.0.3"
  "feelinglight/bareos-sd:23.0.3"
  "feelinglight/bareos-fd:23.0.3"
  "feelinglight/bareos-webui:23.0.3"
)

for image in "${docker_images[@]}"; do
  gitea_package_address="$GITEA_DOMAIN/main/$image"

  docker pull "$image"
  docker tag "$image" "$gitea_package_address"
  docker push "$gitea_package_address"
done


# ------------------------------ single files ------------------------------

upload_file_as_package \
  "https://download.bareos.org/current/windows/winbareos-23.0.4~pre113.6ea98eb40-release-64-bit.exe" \
  "bareos-windows-fd" \
  "23.0.4"

