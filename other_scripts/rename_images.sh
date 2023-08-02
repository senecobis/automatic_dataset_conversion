#!/bin/bash

echo "____renaming imgs to image_left____"

DATAPATH="/data/storage/pellerito/TartanEvent/hospital"
ORIG_DIR="/image_left"
SUB_DIR="/imgs"

for diff in "$DATAPATH"/*/; do
    for seg in "$diff"*/; do
        full_path="$seg"

        if [ -d "$full_path" ]; then
            mv -i "$full_path$SUB_DIR" "$full_path$ORIG_DIR"
        fi


        echo "-------- finished processing segment $seg at difficulty $diff"
    done
done