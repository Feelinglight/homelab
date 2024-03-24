# Bareos

## Установка

- Скачать скрипт **add_bareos_repositories.sh** [отсюда](https://download.bareos.org/current)
  (выбрать нужный дистрибутив)

  The add_bareos_repositories.sh script will:

  - Create a Bareos signature key file /etc/apt/keyrings/bareos-*.gpg.
  - Create the Bareos repository configuration file /etc/apt/sources.list.d/bareos.sources
  - This file refers to the Bareos repository on the download server and to the local /etc/apt/keyrings/bareos-*.gpg file.
  - If authentication credentials are required (https://download.bareos.com) they are stored in the file /etc/apt/auth.conf.d/download_bareos_com.conf.

- Необходимые пакеты:

  - Director: bareos-director, bareos-database-postgresql
  - Storage Daemon: bareos-storage
  - webui: bareos-webui

    Because php-fpm support is not automatically added to Apache2 on Debian like platforms,
    you have to issue those commands to enable it. Replace php8.1-fpm by the version you have
    installed.

    Debian, Ubuntu enabling php8-fpm support on Apache2 example:

    ```bash
    a2enmod proxy_fcgi setenvif
    a2enconf php8.1-fpm
    systemctl reload apache2
    ```

  - On a client: bareos-filedaemon, bareos-traymonitor
  - On a Backup Administration system: bareos-bconsole
    (to have an interactive console to the Bareos Director)
  - Пакет bareos - всё в одном

- Поднять postgres

- Выполнить для postgres

  ```bash
  su postgres -c /usr/lib/bareos/scripts/create_bareos_database
  su postgres -c /usr/lib/bareos/scripts/make_bareos_tables
  su postgres -c /usr/lib/bareos/scripts/grant_bareos_privileges
  ```

- Запуск демонов:

  ```bash
  systemctl enable --now bareos-dir
  systemctl enable --now bareos-sd
  systemctl enable --now bareos-fd
  ```

  Please remark, the Bareos Daemons need to have access to the TCP ports 9101-9103.


## Настройка

- Определения

  A backup job generally consists of a FileSet, a Client, a Schedule for one or several levels or
  times of backups, a Pool.

  Another way of looking at it is the FileSet is what to backup; the Client is who to backup;
  the Schedule defines when, and the Pool defines where (i.e. what Volume).

- Проверка валидности бэкапов:

  ```bash
  su bareos -s /bin/sh -c "/usr/sbin/bareos-dir -t"
  su bareos -s /bin/sh -c "/usr/sbin/bareos-sd -t"
  bareos-fd -t
  bconsole -t
  bareos-tray-monitor -t
  ```

## Конфигурация

### Director


#### Job

- Accurate

  In accurate mode, the File daemon knowns exactly which files were present after the last backup.
  So it is able to handle deleted or renamed files.

- Allow duplicate jobs

- Bootstrap (путь)

- Backup Format

  Tar

- Enabled

- Full/Inc/Diff Pool

- Max Run Sched Time

- File Set

- Job Defs

- Job To Verify

- Level

- ??? Max Concurrent Copies

- Max Full Interval

- Maximum Concurrent Jobs

- Messages

- Pool

- ??? Prune Files (client)
- ??? Prune Jobs (client)
- ??? Prune Volumes (pool)

- ??? Regex Where

- Rerun Failed Levels

- Run After Failed Job
- Run After Job
- Run Before Job
- Run Script

- Purge Migration Job

- Schedule

- Storage (Pool)

- Type

- Write Bootstrap

- Пример

  ```
  Job {
    Name = "Minou"
    Type = Backup
    Level = Incremental
    Client = Minou
    FileSet="Minou Full Set"
    Storage = DLTDrive
    Pool = Default
    Schedule = "MinouWeeklyCycle"
    Messages = Standard
  }
  ```


#### Schedule

- Enabled

- Name

- Run

  The first of every month:

  ```bash
  Schedule {
    Name = "First"
    Run = Level=Full on 1 at 2:05
    Run = Level=Incremental on 2-31 at 2:05
  }
  ```

  Every 10 minutes:

  ```bash
  Schedule {
    Name = "TenMinutes"
    Run = Level=Full hourly at 0:05
    Run = Level=Full hourly at 0:15
    Run = Level=Full hourly at 0:25
    Run = Level=Full hourly at 0:35
    Run = Level=Full hourly at 0:45
    Run = Level=Full hourly at 0:55
  }
  ```


#### FileSet

Trailing слэши нужно добавлять в конце после значений File для папок, когда включены wildcards.
В противном случае не надо.

С помощью команды estimate можно посмотреть какие файлы будут включены в FileSet

- Enable VSS

- Exclude

  ```bash
  FileSet {
    Name = "MyFileSet"
    Include {
      Options {
        Signature = XXH128
      }
      File = /home
      Exclude Dir Containing = .nobackup
    }
  }
  ```

- Include

  - Options

    - Sparse

      ```bash
      Include {
        Options {
          Signature = XXH128
          Sparse = yes
        }
        File = /dev/hd6
      }
      ```

    - Compression

      GZIP - сильное сжатие, медленный
      LZ4HC - как GZIP
      LZ4 - быстрый

    - Signature

      XXH128

    - Wild

      Команда bwild для проверки регулярок

    - Wild Dir
    - Wild File

    - Exclude

    - Ignore case

      Почему то написано что на винде почти всегда оно нужно в yes

    - Shadowing

      Отключает дублирование бэкапа при пересечении правил



- Name


#### Client

- Address (FD Address)

- Enable

- Password (FD Password)

- File Retention

- Hard Quota

- Maximum Concurrent Jobs

- Name

- Soft Quota


#### Storage

- Address (SD Address)

- Collect Statistics

- Device

- Enable

- Maximum Concurrent Jobs

- Media Type (File)

  Написано что они должны быть разные (или что то типа того).

  Подробнее тут https://docs.bareos.org/TasksAndConcepts/VolumeManagement.html#diskchapter

- Name

- Password (SD Password)

- Port (SD Port)


#### Pool

- Action On Purge

- File Retention

- Job Retention

- Label Format

- Maximum Volume Bytes

- Maximum Volumes

- Name

- Next Pool

- Storage

- Volume Retention


#### Catalog

- Address (DB Address)

- Name

- Password (DB Password)

- DB User

- DB Name


### Storage Daemon

#### Storage

- Absolute Job Timeout

- Messages

- Name

- SD Address

#### Director

- Name

- Password

#### Device

- Archive Device

  directory

  Для каждой папки свой Device

- Device Type

  File

- Drive Crypto Enabled

- Media Type

  Вроде должен быть уникальным для каждой папки

- Mount Command

- Mount Point

- Name

- Query Crypto Status

- Random Access

- Removable Media

- Requires Mount

- Unmount Command

- Volume Capacity


### File Daemon

#### Client

- Absolute Job Timeout

- FD Address

- Name

- Pki Cipher


#### Director

- Name

- Password


#### Message

...


### Message

- Append

- Catalog

- Director

- Mail

- Mail Command


## Детали работы

Решение о включении файла в инкремент принимается по st_mtime и st_ctime.

Удаленные файлы будут восстанавливаться, пока не будет сделан следующий полный бэкап.

Без Accurate mode перемещения папок не будут учитываться при инкрементах (файлы в перемещенных
папках не меняют st_mtime и st_ctime).


# Скрипт бэкапов цепочками:

Передать storage из %p и level из %l в скрипт

Если уровень - Full:

bconsole: .api 2

Из команды llist volumes получить все тома пула и jobs которые в них хранятся:
pool_volumes = response['result']['volumes']

Пройти по всем томам пула, узнать какой в них хранится level.

Найти цепочку томов Полный + Инкрементальные

Найти папку, в которой лежат тома

status storage=DockerLinuxStorage

Device status:

Device "DockerLinuxDevice" (/backups/DockerLinux) is not open.

Удалить найденную цепочку



