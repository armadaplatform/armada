#!/bin/bash

backups_dir="/opt/armada/saved_containers_backup"
mkdir -p "${backups_dir}"

source /etc/default/armada

# Wait for recovering and registering services in consul before making first backup.
sleep 60

while [ true ]; do
    now="$(date +%Y-%m-%d_%H-%M-%S)"
    backup_file_name="running_containers_parameters_${now}.json"
    python save_running_containers.py "${backups_dir}/${backup_file_name}" --force
    if [ $[ $RANDOM % 24 ] == 0 ]; then
        if [[ "${SAVED_CONTAINERS_BACKUP_RETENTION}" =~ ^[0-9]+$ ]]; then
            find /opt/armada/saved_containers_backup/ -name 'running_containers_parameters_*.json' -mtime "+${SAVED_CONTAINERS_BACKUP_RETENTION}" -print -delete
        fi
        python /opt/armada-docker/armada_backend/clean_duplicated_saved_containers.py
    fi
    sleep 3600
done
