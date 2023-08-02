#!/bin/bash
echo "____Event conversion____"

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

        cd /home/pellerito/ev-licious
        source ~/anaconda3/etc/profile.d/conda.sh
        conda activate evlicious
        
        echo "-------- Converting EVENTS.h5 folder to single .h5 file"
        python scripts/conversion/convert_to_standard_format.py $event_dir --recursive --divider 1 --height 480 --width 640 --suffix npz --output $event_h_dir_new

        echo "-------- removing $event_dir folder"
        files=$(shopt -s nullglob dotglob; echo $event_dir/*)
        if ((${#files})) && [ -d "$event_h_dir_new" ];then
            rm -r $event_dir
        else 
            echo "-------- empty (or does not exist or is a file)"
        fi

        echo "-------- Converting to single file and generating timestamps"
        cd /home/pellerito/Automatic_dataset_conversion
        conda activate evlicious
        python to_single_file.py --curr_slice=$seg --fps=$fps_n

        echo "-------- Changing back to original folder name"
        image_left_path=$full_path$ORIG_DIR
        imgs_path=$full_path$SUB_DIR
        if [ -d "$imgs_path" ]; then
            mv -i "$imgs_path" "$image_left_path"
        else
            if [ -d "$imgs_path" ];then
                echo "-------- $imgs_path already exists, skipping renaming"
            fi
        fi

        echo "-------- -------- -------- Finished processing segment $seg at difficulty $diff"
    done
done


echo "-------- -------- -------- retriving ids"
for diff in "$DATAPATH"/*/; do
    cd /home/pellerito/Automatic_dataset_conversion
    source ~/anaconda3/etc/profile.d/conda.sh
    conda activate evlicious
    echo "-------- -------- -------- retriving ids for $diff"
    python retrive_ids.py --dataset=$diff --num_events=50000 --timestamp_file_name=timestamps.txt
done