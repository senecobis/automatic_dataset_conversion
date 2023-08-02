#!/bin/bash

echo "____Upsample and generate events"

export CUDA_VISIBLE_DEVICES=0
DATAPATH="/data/storage/pellerito/TartanEvent/gascola"
UPSAMPLED_PATH="/data/storage/pellerito/upsampled/"
ORIG_DIR="/image_left"
EV_SUB_DIR="/events"
RENAMING_H5="/event"
event_file_h5="events.h5"
DEPTH="/depth_left"
SUB_DIR="/imgs"
FPS="/fps.txt"
fps_n=30


for diff in "$DATAPATH"/*/; do
    for seg in "$diff"*/; do
        echo "-------- -------- -------- Processing segment $seg "

        full_path="$seg"
        relative_path=$(realpath --relative-to="$(dirname "$full_path")" "$full_path")
        upsampled_destination="$UPSAMPLED_PATH$relative_path"
        event_dir="$full_path$EV_SUB_DIR"
        event_h_dir_new="$full_path$RENAMING_H5"
        event_file_path="$full_path$event_file_h5"
        image_left_path="$full_path$ORIG_DIR"
        imgs_path="$full_path$SUB_DIR"

        if [ -f "$event_file_path" ]; then
            echo "-------- EVENT file .h5 exists, skipping iteration"
            continue
        else
            echo "-------- EVENT file .h5 do not exists"
        fi

        cd /home/pellerito/rpg_vid2e
        source ~/anaconda3/etc/profile.d/conda.sh        
        conda activate vid2e

        # rename image_left to imgs
        if [ -d "$image_left_path" ]; then
            echo "--------  Renaming $ORIG_DIR to $SUB_DIR"
            mv -i "$image_left_path" "$imgs_path"
        else
            if [ -d "$imgs_path" ];then
                echo "-------- $SUB_DIR already exists, skipping renaming"
            fi
        fi

        if test -f "$full_path$FPS"; then
            echo "-------- fps file exists in $full_path"
        else
            echo "-------- fps file DO NOT EXISTS in $full_path: creating fps file"
            echo "$fps_n" > "$full_path$FPS"
        fi

        if [ -d "$upsampled_destination" ]; then
            echo "-------- UPSAMPLE folder exists"
        else
            echo "-------- UPSAMPLE do not exists"
        fi

        if [ -d "$event_h_dir_new" ]; then
            echo "-------- EVENT .h5 exists in $event_dir"
        else
            echo "-------- EVENT .h5 do not exists"
        fi

        if [ -d "$event_dir" ]; then
            echo "-------- EVENT folder exists in $event_dir"
        else
            echo "-------- EVENT folder do not exists"
        fi
        
        # if no events or upsampled folder exists, then upsample and generate events

        if [ -d "$upsampled_destination" ] || [ -d "$event_h_dir_new" ]; then
            echo "-------- No need to upsample $full_path"
        else
            python upsampling/upsample.py --input_dir=$full_path --output_dir=$upsampled_destination --num_bisections=2
            rm -r "$upsampled_destination$DEPTH"
        fi

        if [ -d "$event_dir" ] || [ -d "$event_h_dir_new" ]; then
            echo "-------- EVENTS or EVENT folder exists no need to generate events"
        else
            python esim_torch/scripts/generate_events.py --input_dir=$upsampled_destination --output_dir=$event_dir --contrast_threshold_neg=0.2 --contrast_threshold_pos=0.2 --refractory_period_ns=0
        fi

        echo "-------- Removing upsampled folder"
        if [ -d "$upsampled_destination" ]; then
            rm -r "$upsampled_destination"
        else
            echo "-------- No upsampled folder to remove"
        fi

        echo "-------- -------- -------- Finished processing segment $seg at difficulty $diff"
    done
done