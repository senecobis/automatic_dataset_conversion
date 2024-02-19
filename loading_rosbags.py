import os
import cv2
import rosbag
import argparse
import numpy as np
from pathlib import Path
from bagpy import bagreader
import matplotlib.pyplot as plt
from sensor_msgs.msg import Image
from retrive_ids import compute_ids
from scipy.spatial.transform import Slerp
from scipy.spatial.transform import Rotation
from evlicious.io.h5_event_handle import H5EventHandle
from evlicious.io.rosbag_event_handle import RosbagEventHandle


def subdataset_path(rosbag_path):
    # get the entire file name from path without extension
    file_name = os.path.splitext(os.path.basename(rosbag_path))[0]
    #get the file path without the file name
    dirname = os.path.dirname(rosbag_path)
    return os.path.join(dirname, file_name)


def extract_poses(bag_path, topic):
    sub_dataset_path = subdataset_path(bag_path)
    if not os.path.exists(sub_dataset_path):
        os.makedirs(sub_dataset_path)

    poses_path = os.path.join(sub_dataset_path, "poses.txt")
    timestamp_pose_path = os.path.join(sub_dataset_path, "timestamps_poses.txt")
        
    bag = rosbag.Bag(bag_path, "r")
    for topic_, msg, t in bag.read_messages(topics=[topic]):
        if topic_ != topic:
            continue
        timestamp = t.to_nsec()
        x = msg.pose.position.x
        y = msg.pose.position.y
        z = msg.pose.position.z
        qx = msg.pose.orientation.x
        qy = msg.pose.orientation.y
        qz = msg.pose.orientation.z
        qw = msg.pose.orientation.w

        with open(poses_path, "a") as f:
            f.write(f"{x} {y} {z} {qx} {qy} {qz} {qw}\n")
        with open(timestamp_pose_path, "a") as f:
            f.write(f"{timestamp/1000}\n")

    bag.close()
    return


def image_extractor_from_rosbag(bag_path, topic, image_folder_name):
    sub_dataset_path = subdataset_path(bag_path)
    output_folder = os.path.join(sub_dataset_path, image_folder_name)
    timestamp_img_path = os.path.join(sub_dataset_path, f"timestamps_{image_folder_name}.txt")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    count = 0
    bag = rosbag.Bag(bag_path, "r")
    for topic, msg, t in bag.read_messages(topics=[topic]):
        if topic != topic:
            continue
        # Extract the image data from ROS message
        img_data = np.frombuffer(msg.data, dtype=np.uint8)

        try:
            img_shape = (msg.height, msg.width, 3) # Assuming color image
            cv_image = img_data.reshape(img_shape)
        except:
            img_shape = (msg.height, msg.width, 1) # Assuming grayscale image
            cv_image = img_data.reshape(img_shape)
        


        # Save the image to file
        img_path = os.path.join(output_folder, "%06i.png" % count)
        cv2.imwrite(img_path, cv_image)

        with open(timestamp_img_path, "a") as f:
            f.write(f"{t.to_nsec()/1000}\n")

        count += 1
    bag.close()

def save_poses_relative_to_imgs(bag_path, image_folder_name):
    sub_dataset_path = subdataset_path(bag_path)
    timestamp_img_path = os.path.join(sub_dataset_path, f"timestamps_{image_folder_name}.txt")
    timestamp_poses_path = os.path.join(sub_dataset_path, "timestamps_poses.txt")
    poses_path =  os.path.join(sub_dataset_path, "poses.txt")
    interpolate_poses_path = os.path.join(sub_dataset_path, f"poses_interp_{image_folder_name}.txt")

    poses = np.loadtxt(poses_path)
    timestamp_img = np.loadtxt(timestamp_img_path)
    timestamp_poses = np.loadtxt(timestamp_poses_path)
    # search timestamps of the images inside poses (poses more frequent)
    poses_interpolated = interpolate_poses(poses, target_timestamps=timestamp_img, original_timestamps=timestamp_poses)
    np.savetxt(interpolate_poses_path, poses_interpolated)


def interpolate_pose(pose1, pose2, tstamp1, tstamp2, target_time):
    alpha = (target_time - tstamp1) / (tstamp2 - tstamp1)

    x_before, y_before, z_before, qx_before, qy_before, qz_before, qw_before = pose1
    x_after, y_after, z_after, qx_after, qy_after, qz_after, qw_after = pose2

    # Perform linear interpolation for position (x, y, z)
    x_interpolated = x_before + alpha * (x_after - x_before)
    y_interpolated = y_before + alpha * (y_after - y_before)
    z_interpolated = z_before + alpha * (z_after - z_before)

    # Perform linear interpolation for quaternion (qx, qy, qz, qw)
    R_before = Rotation.from_quat([qx_before, qy_before, qz_before, qw_before]).as_matrix()
    R_after = Rotation.from_quat([qx_after, qy_after, qz_after, qw_after]).as_matrix()
    key_rots = Rotation.from_matrix(np.stack((R_before, R_after), axis=0))

    slerp = Slerp([tstamp1, tstamp2], key_rots)
    interp_rots = slerp(target_time)
    q_interpolated = interp_rots.as_quat()
    
    return (x_interpolated, y_interpolated, z_interpolated, *q_interpolated)


def interpolate_single_pose(poses, target_time, original_timestamps):
    index_before = np.searchsorted(original_timestamps, target_time) - 1
    index_after = index_before + 1

    # handle edge case of target time is 
    # after the last t or before the first t of original t stamps
    if index_after >= len(original_timestamps):
        return poses[index_before]
    if index_before < 0:
        return poses[index_after]

    return interpolate_pose(pose1=poses[index_before], 
                            pose2=poses[index_after], 
                            tstamp1=original_timestamps[index_before], 
                            tstamp2=original_timestamps[index_after], 
                            target_time=target_time
                            )


def interpolate_poses(poses, target_timestamps, original_timestamps):
    interpolated_trajectory = []
    for target_time in target_timestamps:
        interpolated_pose = interpolate_single_pose(poses, target_time, original_timestamps)
        interpolated_trajectory.append(interpolated_pose)
    return np.stack(interpolated_trajectory, axis=0)


def get_events_from_rosbag(rosbag_path):
    output_dir = subdataset_path(rosbag_path)
    h5_path = Path(os.path.join(output_dir, "events.h5"))
    if h5_path.exists():
        return h5_path
    rosbag_handle = RosbagEventHandle.from_path(rosbag_path)
    events = rosbag_handle.get_between_idx(0, rosbag_handle.num_events[-1])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    events.to(h5_path)
    return h5_path

def render_events(rosbag_path, output_folder):
    rosbag_handle = RosbagEventHandle.from_path(rosbag_path)
    output_folder = "/home/pellerito/Automatic_dataset_conversion/DEBUG"
    indices = np.loadtxt("/data/storage/pellerito/StereoDavis/monitor1/indices_left.txt", delimiter=",")
    i0 = indices[0]
    i1 = indices[1]
    for ind, img in enumerate(sorted(os.listdir("/data/storage/pellerito/StereoDavis/monitor1/images_left"))):
        plt.clf()
        image = cv2.imread(os.path.join("/data/storage/pellerito/StereoDavis/monitor1/images_left",img), cv2.IMREAD_GRAYSCALE)
        event = rosbag_handle.get_between_idx(i0[ind], i1[ind])
        rendered = event.render(np.moveaxis(np.stack((image, image, image)), 0, -1))
        plt.imshow(rendered)
        plt.savefig(os.path.join(output_folder, "%06i.png" % ind))

def remove_topic_from_rosbag(input_bagfile, output_bagfile, topic_to_remove='/davis_left/events'):
    with rosbag.Bag(output_bagfile, 'w') as output_bag:
        for topic, msg, t in rosbag.Bag(input_bagfile).read_messages():
            if topic != topic_to_remove:
                output_bag.write(topic, msg, t)

def rename_files():
    # iterate over the folders in a dataset 
    for paths in os.walk(args.dataset):
        data_path, _, files_path = paths
        for file in files_path:
            if file in ("indices_left.txt", "indices_right.txt"):
                os.rename(os.path.join(data_path, file), os.path.join(data_path, "indices.txt"))
            if file in ("poses_interp_images_left.txt", "poses_interp_images_right.txt", "poses_left.txt"):
                os.rename(os.path.join(data_path, file), os.path.join(data_path, "pose_left.txt"))

    for paths in os.walk(args.dataset):
        data_path, _, files_path = paths
        if os.path.basename(data_path) in ("images_left", "images_right"):
            os.rename(data_path, os.path.join(os.path.dirname(data_path), "image_left"))

    # get the entire file name from path without extension




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=None, type=str, help="Current slice to process")
    parser.add_argument("--num_events", default=50000, type=int, help="number of events before the last image")
    parser.add_argument("--indices_file_name", default="indices.txt", type=str, help="name of the file where the indices are stored")
    args=parser.parse_args()

    # iterate over the folders in a dataset 
    for paths in os.walk(args.dataset):
        data_path, _, files_path = paths
        # iterate over the files in a folder
        for file in files_path:
            # check if the file is a rosbag
            if file.endswith(".bag"):
                # get the path of the rosbag
                rosbag_path = os.path.join(data_path, file)
                # get the topics of the rosbag
                b = bagreader(rosbag_path)
                print(b.topic_table)

                # get events from rosbag
                events_path = get_events_from_rosbag(rosbag_path)
                dataset_path = subdataset_path(rosbag_path)
                timestamps_left = Path(os.path.join(dataset_path, "timestamps_images_left.txt"))
                timestamps_right = Path(os.path.join(dataset_path, "timestamps_images_right.txt"))
                indices_left = Path(os.path.join(dataset_path, "indices_left.txt"))
                indices_right = Path(os.path.join(dataset_path, "indices_right.txt"))

                # extract the poses from the rosbag
                extract_poses(rosbag_path, topic="/optitrack/davis_stereo")

                if "/davis_left/events" in dict(b.topic_table["Topics"]).values():
                    image_extractor_from_rosbag(rosbag_path, topic="/davis_left/image_raw", image_folder_name="images_left")
                    compute_ids(event_file_path=events_path, indices_file_path=indices_left, image_timestamps_file_path=timestamps_left, num_events=args.num_events)
                    # save the poses relative to the images
                    save_poses_relative_to_imgs(rosbag_path, image_folder_name="images_left")
                elif "/davis_right/events" in dict(b.topic_table["Topics"]).values():
                    image_extractor_from_rosbag(rosbag_path, topic="/davis_right/image_raw", image_folder_name="images_right")
                    compute_ids(event_file_path=events_path, indices_file_path=indices_right, image_timestamps_file_path=timestamps_right, num_events=args.num_events)
                    # save the poses relative to the images
                    save_poses_relative_to_imgs(rosbag_path, image_folder_name="images_right")
