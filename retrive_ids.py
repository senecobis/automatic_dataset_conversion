
""" This script is used to retrive the ids of the events that are in the same window of the image."""

""" Summary of the dataset structure:

    dataset
    ├── segment_0
    │   ├── events.h5
    │   ├── indices.txt
    │   ├── timestamps.txt
    │   └── K.yaml
    ├── segment_1
    │   ├── events.h5
    │   ├── indices.txt
    │   ├── timestamps.txt
    │   └── K.yaml
    ├── segment_2
    ...
    └── segment_n
"""

import evlicious
from pathlib import Path
import tqdm
import h5py
import numpy as np
import os
import yaml
import argparse

TYPES = dict(_x=np.uint16, _y=np.uint16, t=np.int64, p=np.int8, x=np.uint16, y=np.uint16)

def open_intrinsics(K_path):
        with open(K_path, 'r') as file:
            data = yaml.safe_load(file)

        # Extract the intrinsics
        intrinsics = data['cam0']['intrinsics']
        resolution = data['cam0']['resolution']

        print("Using intrinsics from {}".format(K_path), intrinsics)
        return intrinsics, resolution

def add_group_to_custom_dataset(handle, K_file):
    intrinsics, resolution = open_intrinsics(K_file)

    ev = handle.create_group("events")
    ev.create_dataset("divider", data=1)
    ev.create_dataset("width", data=resolution[0])
    ev.create_dataset("height", data=resolution[1])
    ev.create_dataset("x", data=handle["x"])
    ev.create_dataset("y", data=handle["y"])
    ev.create_dataset("t", data=handle["t"])
    ev.create_dataset("p", data=handle["p"])

    del handle["x"]
    del handle["y"]
    del handle["t"]
    del handle["p"]

    return handle

def cast_dataset_to(handle, type_x = np.uint16, type_y = np.uint16, type_t = np.int64, type_p = np.int8):
    # if not type_ in TYPES.values():
    #     raise ValueError(f"Type {type_} not supported, try with {TYPES.values()}")
    
    data_type = handle["events"]["x"].dtype
    if data_type != type_x:
        print(f"Casting x to {type_x} from {data_type} ")
        a = handle["events"]["x"].astype(type_x)[:]
        del handle["events"]["x"]
        handle["events"].create_dataset("x", data=a)
        print(f"Data casted to {handle['events']['x'].dtype}")

    data_type = handle["events"]["y"].dtype
    if data_type != type_y:
        print(f"Casting y to {type_y} from {data_type} ")
        a = handle["events"]["y"].astype(type_y)[:]
        del handle["events"]["y"]
        handle["events"].create_dataset("y", data=a)
        print(f"Data casted to {handle['events']['y'].dtype}")
   
    data_type = handle["events"]["t"].dtype
    if data_type != type_t:
        print(f"Casting t to {type_t} from {data_type} ")
        a = handle["events"]["t"].astype(type_t)[:]
        del handle["events"]["t"]
        handle["events"].create_dataset("t", data=a)
        print(f"Data casted to {handle['events']['t'].dtype}")

    data_type = handle["events"]["p"].dtype
    if data_type != type_p:
        print(f"Casting p to {type_p} from {data_type} ")
        a = handle["events"]["p"].astype(type_p)[:]
        del handle["events"]["p"]
        handle["events"].create_dataset("p", data=a)
        print(f"Data casted to {handle['events']['p'].dtype}")

    return handle

def compute_ids(event_file_path, indices_file_path, image_timestamps_file_path, num_events):
    if indices_file_path.exists():
        print(f"{indices_file_path} already exists, skipping...")
        return
    event = evlicious.io.load_events_from_path(event_file_path)
    image_timestamps = np.genfromtxt(image_timestamps_file_path).astype(int)
    image_index_to_window_end = event.find_index_from_timestamp(image_timestamps)
    image_index_to_window_start = np.clip(image_index_to_window_end - num_events, 0, len(event)-1) 
    np.savetxt(indices_file_path, (image_index_to_window_start, image_index_to_window_end), delimiter=',')
    print(f"saved in {indices_file_path}")
     

def cut_dataset_by_nearest_timestamp(event_file_path, start_tstamp=None, end_tstamp=None):
    print(f"Cutting dataset from {start_tstamp} to {end_tstamp}")
    handle = h5py.File(str(event_file_path), "r+")
    if not "events" in handle.keys():
        raise ValueError("events is not a key in the h5 file")
    else:
        data_x = handle["events"]["x"][:]
        data_y = handle["events"]["y"][:]
        data_t = handle["events"]["t"][:]
        data_p = handle["events"]["p"][:]

        print("Data shape before cutting", data_x.shape)
        print("Data shape before cutting", data_y.shape)
        print("Data shape before cutting", data_t.shape)
        print("Data shape before cutting", data_p.shape)

        if start_tstamp is not None:
            start_index = np.argmin((data_t - start_tstamp)**2)
        else:
            start_index = 0
        if end_tstamp is not None:
            end_index = np.argmin((data_t - end_tstamp)**2)
        else:
            end_index = -1
        
        new_x = data_x[start_index:end_index]
        new_y = data_y[start_index:end_index]
        new_t = data_t[start_index:end_index]
        new_p = data_p[start_index:end_index]

        print("Data shape after cutting", new_x.shape)
        print("Data shape after cutting", new_y.shape)
        print("Data shape after cutting", new_t.shape)
        print("Data shape after cutting", new_p.shape)

        del handle["events"]["x"]
        del handle["events"]["y"]
        del handle["events"]["t"]
        del handle["events"]["p"]

        print("Delete old data")

        handle.create_dataset("x", data=new_x)
        handle.create_dataset("y", data=new_y)
        handle.create_dataset("t", data=new_t)
        handle.create_dataset("p", data=new_p)
        
        print("Data saved")
        
    

def process_dataset(dataset, num_events, indices_file_name="indices.txt", timestamp_file_name="timestamps.txt"):
    for segments in tqdm.tqdm(os.scandir(dataset), ncols=50):
        segment_dir = Path(segments.path)
        event_file_path = segment_dir / Path("events.h5")
        indices_file_path=segment_dir / Path(indices_file_name)
        image_timestamps_file_path=segment_dir / Path(timestamp_file_name)

        print(f"Processing ... {event_file_path}")
        if not event_file_path.is_file():
            print("NO events.h5 file found SKIPPING ID RETRIVAL...")
            continue
            
        handle = h5py.File(str(event_file_path), "r+")
        if not "events" in handle.keys():
            print("events is not a key in the h5 file, replacing and adding key")
            handle = add_group_to_custom_dataset(handle, K_file=segment_dir / Path("K.yaml"))
        handle = cast_dataset_to(handle)
        handle.close()

        compute_ids(event_file_path=event_file_path, 
                    indices_file_path=indices_file_path, 
                    image_timestamps_file_path=image_timestamps_file_path, 
                    num_events=num_events
                    )



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=None, type=str, help="Current slice to process")
    parser.add_argument("--num_events", default=50000, type=int, help="number of events before the last image")
    parser.add_argument("--indices_file_name", default="indices.txt", type=str, help="name of the file where the indices are stored")
    parser.add_argument("--timestamp_file_name", default="timestamps.txt", type=str, help="name of the file where the timestamps are stored")
    args=parser.parse_args()

    process_dataset(dataset=args.dataset, num_events=args.num_events, indices_file_name=args.indices_file_name, timestamp_file_name=args.timestamp_file_name)