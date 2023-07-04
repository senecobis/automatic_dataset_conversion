#!/bin/bash

echo "____renaming imgs to image_left____"
DATAPATH=/data/storage/pellerito/TartanAir/
DATASET=("abandonedfactory/" "abandonedfactory_night/" "amusement/" "carwelding/" "endofworld/" "gascola/")
SEGMENTS=("P000" "P001" "P002" "P003" "P004" "P005" "P006" "P007" "P008" "P009" "P010" "P011" "P012" "P013" "P014")
DIFFICULTY=("Easy/" "Hard/")
ORIG_DIR="/image_left"
SUB_DIR="/imgs"
DEPTH="/depth_left"
EV_FILE="/events.h5"
TIMESTAMPS="/timestamps.txt"


for datasetname in ${DATASET[@]}; do
    for diff in ${DIFFICULTY[@]}; do
        for seg in ${SEGMENTS[@]}; do
            full_path="$DATAPATH$DATASET$diff$seg"

            if [ -d "$full_path" ]; then
                echo "-------- processing $full_path"

                if [ -d "$full_path$ORIG_DIR" ]; then
                    echo "-----------  $ORIG_DIR exists"
                else
                    echo "-----------  $ORIG_DIR do not exist"
                    if [ -d "$full_path$SUB_DIR" ]; then
                        echo "----------- but $SUB_DIR exists, CHECK DATASET"
                    fi
                fi

                if [ -d "$full_path$DEPTH" ]; then
                    echo "-----------  $DEPTH exists"
                else
                    echo "-----------  $DEPTH do not exist, CHECK DATASET"
                fi


                if test -f "$full_path$EV_FILE"; then
                    echo "----------- $EV_FILE exists in folder"
                else
                    echo "----------- $EV_FILE do not exist  in folder, CHECK DATASET"
                fi

                if test -f "$full_path$TIMESTAMPS"; then
                    echo "----------- $TIMESTAMPS exists in folder"
                else
                    echo "----------- $TIMESTAMPS do not exist in folder, CHECK DATASET"
                fi

            fi

        done
    done
done