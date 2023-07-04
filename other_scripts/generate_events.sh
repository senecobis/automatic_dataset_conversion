#!/bin/bash

echo "____Upsample and generate events as .npz files____"

export CUDA_VISIBLE_DEVICES=0
DATAPATH="/data/storage/pellerito/MoonLanding"
UPSAMPLED_PATH="/data/storage/pellerito/upsampled/"
ORIG_DIR="/image_left"
EV_SUB_DIR="/events"
RENAMING_H5="/event"
DEPTH="/depth_left"
SUB_DIR="/imgs"
FPS="/fps.txt"


for diff in "$DATAPATH"/*/; do
    for seg in "$diff"*/; do

        echo "-------- Processing segment $seg "

        full_path="$seg"
        relative_path=$(realpath --relative-to="$(dirname "$full_path")" "$full_path")

        upsampled_destination="$UPSAMPLED_PATH$relative_path"
        event_dir="$full_path$EV_SUB_DIR"
        event_h_dir_new="$full_path$RENAMING_H5"

        cd /home/pellerito/rpg_vid2e

        # Check an moove folders

        if [ -d "$full_path$ORIG_DIR" ]; then
            mv -i "$full_path$ORIG_DIR" "$full_path$SUB_DIR"
            echo "--------  Renaming $ORIG_DIR to $SUB_DIR"
        else
            if [ -d "$full_path$SUB_DIR" ];then
                echo "-------- $SUB_DIR already exists, skipping renaming"
            fi
        fi

        if test -f "$full_path$FPS"; then
            echo "-------- fps file exists in $full_path"
        else
            echo "-------- fps file DO NOT EXISTS in $full_path: CRASHING"
        fi

        if [ -d "$upsampled_destination" ]; then
            echo "UPSAMPLE folder exists"
        else
            echo "UPSAMPLE do not exists"
        fi

        if [ -d "$event_h_dir_new" ]; then
            echo "EVENT .h5 exists in $event_dir"
        else
            echo "EVENT .h5 do not exists"
        fi
        
        # if no events or upsampled folder exists, then upsample and generate events

        if [ -d "$upsampled_destination" ] || [ -d "$event_h_dir_new" ]; then
            echo "no need to upsample $full_path"
        else
            python upsampling/upsample.py --input_dir=$full_path --output_dir=$upsampled_destination --num_bisections=2
            rm -r "$upsampled_destination$DEPTH"
        fi

        if [ -d "$event_dir" ] || [ -d "$event_h_dir_new" ]; then
            echo "EVENTS or EVENT folder exists in $event_dir"
        else
            python esim_torch/scripts/generate_events.py --input_dir=$upsampled_destination --output_dir=$event_dir --contrast_threshold_neg=0.2 --contrast_threshold_pos=0.2 --refractory_period_ns=0
        fi

        echo "-------- finished processing segment $seg at difficulty $diff"
    done
done