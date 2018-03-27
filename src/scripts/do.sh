#!/bin/bash

if [[ "$1" == "retrieve_data" || "$1" == "retrieve_ref" || "$1" == "process" ]] ; then
    shift
    shift
    python index.py "$*"

elif [[ "$1" == "search" ]] ; then
    shift
    shift
    python search.py "$*"
elif [[ "$1" == "refresh" ]] ; then
    if ! [[ -e $main_dir/db_map.json ]] ; then
        touch $main_dir/db_map.json
    fi
    shift
    shift
    python database.py map
    chmod 755 $main_dir/db_map.json
else
    echo 'Invalid command.'
    exit 1
fi
