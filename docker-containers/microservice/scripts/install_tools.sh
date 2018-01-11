#!/usr/bin/env bash

DIR="$(dirname "${BASH_SOURCE[0]}")/tools"

for file in $DIR/*; do
    filename="${file##*/}"
    case ${file##*.} in
        'sh')
            ln -s $file /usr/local/bin/${filename%.*}
            ;;
        'bashrc')
            echo -e "\n" >> /etc/bash.bashrc
            cat $file >> /etc/bash.bashrc
            ;;
    esac
done

