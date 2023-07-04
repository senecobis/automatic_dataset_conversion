import glob
import tqdm
import shutil
import argparse
import evlicious
import os.path as osp
from pathlib import Path
from evlicious.io.utils.h5_writer import H5Writer


def create_timestamps_file(scene, fps_images):
    print(f"\n Processing {scene}")

    images_path = Path(scene + '/imgs')
    if not Path(images_path).is_dir():
        print(f"{images_path} do not exist")
        images_path = Path(scene + '/image_left')
        if not Path(images_path).is_dir():
            print(f"{images_path} do not exist, no image file...quitting")
            return

    image_files = sorted(glob.glob(osp.join(images_path, '*.png')))
    image_timestamps_file_path = scene + '/timestamps.txt'

    if not Path(scene).is_dir():
        print(f"{scene} do not exist")
        return

    # creates timestamps for images
    with open(image_timestamps_file_path, 'w') as f:
        for ind, _ in enumerate(image_files):
            timestamp=(1/fps_images)*ind*1e9
            if ind == 0:
                f.writelines(f"{timestamp}")
            else:
                f.writelines(f"\n{timestamp}")
        f.close()
    
    print(f"\n Finished processing {scene}")


def to_single_file(scene, fps_images):
    print(f"\n Processing {scene}")

    event_files = sorted(glob.glob(osp.join(scene, 'event/*.h5')))
    outfile = Path(scene + "/events.h5")

    images_path = Path(scene + '/imgs')
    if not Path(images_path).is_dir():
        print(f"{images_path} do not exist")
        images_path = Path(scene + '/image_left')
        if not Path(images_path).is_dir():
            print(f"{images_path} do not exist, no image file...quitting")
            return

    image_files = sorted(glob.glob(osp.join(images_path, '*.png')))
    image_timestamps_file_path = scene + '/timestamps.txt'


    if not Path(scene).is_dir():
        print(f"{scene} do not exist")
        return

    # creates timestamps for images
    with open(image_timestamps_file_path, 'w') as f:
        for ind, _ in enumerate(image_files):
            timestamp=(1/fps_images)*ind*1e9
            if ind == 0:
                f.writelines(f"{timestamp}")
            else:
                f.writelines(f"\n{timestamp}")
        f.close()
    
    event_folder = Path(scene+"/event")
    if not event_folder.is_dir():
        print(f"{event_folder} is not dir")
        return
    if Path(outfile).is_file():
        return

    # Transform to single file .h5
    writer = H5Writer(outfile)
    for path in tqdm.tqdm(event_files, ncols=50):
        events = evlicious.io.load_events_from_path(Path(path)).load()
        writer.add_data(events)


    print(f"\n Finished processing {scene}")
    event_directory=osp.join(scene, 'event')
    shutil.rmtree(event_directory)
    print(f"\n removed... {event_directory}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--curr_slice", default=None, type=str, help="Current slice to process")
    parser.add_argument("--fps", default=None, type=int, help="fps of the images")
    args=parser.parse_args()

    to_single_file(scene=args.curr_slice, fps_images=args.fps)