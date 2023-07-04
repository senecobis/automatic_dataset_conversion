import glob
import tqdm
import shutil
import argparse
import evlicious
import os.path as osp
from pathlib import Path

def create_timestamps_file(scene, fps_images, tstamps_multiplier=0, img_extension='.png'):
    print(f"\n Processing {scene}")

    images_path = Path(scene + '/imgs')
    if not Path(images_path).is_dir():
        print(f"{images_path} do not exist")
        images_path = Path(scene + '/image_left')
        if not Path(images_path).is_dir():
            print(f"{images_path} do not exist, no image file...quitting")
            return

    image_files = sorted(glob.glob(osp.join(images_path, f'*{img_extension}')))
    image_timestamps_file_path = scene + '/timestamps.txt'

    if not Path(scene).is_dir():
        print(f"{scene} do not exist")
        return

    # creates timestamps for images
    ind = 0
    with open(image_timestamps_file_path, 'w') as f:
        for file in image_files:
            timestamp=(1/fps_images)*ind*1e9
            if ind == 0:
                f.writelines(f"{timestamp}")
            else:
                f.writelines(f"\n{timestamp}")
            ind += 1
            if tstamps_multiplier > 0:
                for _ in range(int(tstamps_multiplier)):
                    timestamp=(1/fps_images)*ind*1e9
                    f.writelines(f"\n{timestamp}")
                    ind += 1
        f.close()
    
    print(f"\n Finished processing {scene}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", type=str, required=True)
    parser.add_argument("--fps", type=float, required=True)
    parser.add_argument("--tstamps_multiplier", type=float, required=True)
    parser.add_argument("--img_extension", type=str, required=True)
    args = parser.parse_args()

    create_timestamps_file(scene=args.scene, fps_images=args.fps, tstamps_multiplier=args.tstamps_multiplier, img_extension=args.img_extension)
