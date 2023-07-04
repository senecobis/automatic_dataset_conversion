#!/bin/bash

echo "____Convert to .h5 file____"


DATAPATH="/data/storage/pellerito/TartanEventRest"
ORIG_DIR="/image_left"
SUB_DIR="/imgs"
EV_SUB_DIR="/events"
FPS="/fps.txt"
RENAMING_H5="/event"

for diff in "$DATAPATH"/*/; do
    for seg in "$diff"*/; do

        echo "-------- Processing segment $seg "

        full_path="$seg"
        event_dir="$full_path$EV_SUB_DIR"
        event_h_dir_new="$full_path$RENAMING_H5"

        if [ -d "$full_path$ORIG_DIR" ]; then
            mv -i "$full_path$ORIG_DIR" "$full_path$SUB_DIR"
            echo "--------  Renaming $ORIG_DIR to $SUB_DIR"
        else
            if [ -d "$full_path$SUB_DIR" ];then
                echo "-------- $SUB_DIR already exists, skipping renaming"
            fi
        fi

        cd /home/pellerito/ev-licious
        
        python scripts/conversion/convert_to_standard_format.py $event_dir --recursive --divider 1 --height 480 --width 640 --suffix npz --output $event_h_dir_new

        files=$(shopt -s nullglob dotglob; echo $event_dir/*)
        if ((${#files}));then
            echo "-------- contains files, removing $event_dir folder"
            rm -r $event_dir
        else 
            echo "-------- empty (or does not exist or is a file)"
        fi
        echo "-------- finished processing segment $seg at difficulty $diff"
        
    done
done