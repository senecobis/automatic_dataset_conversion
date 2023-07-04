#!/bin/bash

echo "____renaming imgs to image_left____"
# SEGMENTS=("P000" "P001" "P002" "P003" "P004" "P005" "P006" "P007" "P008" "P009" "P010" "P011" "P012" "P013" "P014")
# DIFFICULTY=("Easy/" "Hard/")
# DATAPATH=/data/storage/pellerito/TartanAir/gascola/
SEGMENTS=("P012" "P013")
DIFFICULTY=("Hard/")
DATAPATH="/data/storage/pellerito/TartanAir/abandonedfactory_night/"
ORIG_DIR="/image_left"
SUB_DIR="/imgs"

for diff in ${DIFFICULTY[@]}; do
    for seg in ${SEGMENTS[@]}; do
        full_path="$DATAPATH$diff$seg"


        if [ -d "$full_path" ]; then
            mv -i "$full_path$SUB_DIR" "$full_path$ORIG_DIR"
        fi


        echo "-------- finished processing segment $seg at difficulty $diff"
    done
done