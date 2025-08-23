#!/bin/bash

# Скрипт запускается вручную!!

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

# ------------------------------ apt-mirror ------------------------------

# Конфигурация apt-mirror составляется каждый раз заново. Каждый сервис может дописать в
# конфигурацию адреса deb-репозиториев. apt-mirror запускается в конце этого скрипта.
apt_mirror_dir="$MIRRORS_DIR/apt-mirror"

mkdir -p "$apt_mirror_dir"
mkdir -p "$apt_mirror_dir/mirror"
mkdir -p "$apt_mirror_dir/var"
mkdir -p "$apt_mirror_dir/skel"

echo "set base_path $apt_mirror_dir"    | sudo tee /etc/apt/mirror.list
echo "set nthreads     20"              | sudo tee -a /etc/apt/mirror.list
echo "set _tilde 0"                     | sudo tee -a /etc/apt/mirror.list

# ------------------------------ docker images ------------------------------

echo "Вход в учетку gitea:"
docker login "$GITEA_DOMAIN"

docker_images=(
  "juanluisbaptiste/postfix:1.7.1"
  "feelinglight/bareos-dir:23.0.3"
  "feelinglight/bareos-sd:23.0.3"
  "feelinglight/bareos-fd:23.0.3"
  "feelinglight/bareos-webui:23.0.3"
  "feelinglight/bareos-dir:24.0.5-pre32.7c5f79a1e"
  "feelinglight/bareos-sd:24.0.5-pre32.7c5f79a1e"
  "feelinglight/bareos-fd:24.0.5-pre32.7c5f79a1e"
  "feelinglight/bareos-webui:24.0.5-pre32.7c5f79a1e"
)

for image in "${docker_images[@]}"; do
  gitea_package_address="$GITEA_DOMAIN/main/$image"

  docker pull "$image"
  docker tag "$image" "$gitea_package_address"
  docker push "$gitea_package_address"
done


# ------------------------------ single files ------------------------------

# Перенесено в bareos
# upload_file_as_package \
#   "https://download.bareos.org/current/windows/winbareos-23.0.4~pre113.6ea98eb40-release-64-bit.exe" \
#   "bareos-windows-fd" \
#   "23.0.4"


# ------------------------------ bareos ------------------------------

bareos_resources=(
  "https://download.bareos.org/current/BareosMainReference/"
  "https://download.bareos.org/current/Debian_12/"
  "https://download.bareos.org/current/windows/"
  "https://download.bareos.org/current/xUbuntu_22.04/"
  "https://download.bareos.org/current/xUbuntu_24.04/"
)

for res in "${bareos_resources[@]}"; do
  wget -r --no-parent "$res" -P "$MIRRORS_DIR/bareos/site-24.0.5-pre32.7c5f79a1e"
done

echo "deb-src https://download.bareos.org/current/xUbuntu_24.04 / "     | sudo tee -a /etc/apt/mirror.list
echo "deb https://download.bareos.org/current/xUbuntu_24.04 / "         | sudo tee -a /etc/apt/mirror.list

echo "deb-src https://download.bareos.org/current/xUbuntu_22.04 / "     | sudo tee -a /etc/apt/mirror.list
echo "deb https://download.bareos.org/current/xUbuntu_22.04 / "         | sudo tee -a /etc/apt/mirror.list

echo "deb-src https://download.bareos.org/current/Debian_12/ / "        | sudo tee -a /etc/apt/mirror.list
echo "deb https://download.bareos.org/current/Debian_12/ / "            | sudo tee -a /etc/apt/mirror.list


# ------------------------------ apt-mirror run ------------------------------

apt-mirror

