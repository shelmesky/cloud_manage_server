#!/bin/bash

inotifywait -mrq --event access,create,delete,modify,move,attrib /var/lib/pnp4nagios/perfdata/localhost | while read D E F; do
    if [ "$e" = "IGNORED" ]; then
        continue
    fi
    echo $D $E $F
done
