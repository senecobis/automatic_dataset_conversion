import os
from sensor_msgs.msg import Image
import argparse
import rosbag
import numpy as np
import cv2
from pathlib import Path
from scipy.spatial.transform import Rotation
from scipy.spatial.transform import Slerp
from evlicious.io.rosbag_event_handle import RosbagEventHandle
from evlicious.io.h5_event_handle import H5EventHandle


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
            f.write(f"{timestamp}\n")

    bag.close()
    return


def image_extractor_from_rosbag(bag_path, image_topic, image_folder_name):
    sub_dataset_path = subdataset_path(bag_path)
    output_folder = os.path.join(sub_dataset_path, image_folder_name)
    timestamp_img_path = os.path.join(sub_dataset_path, f"timestamps_{image_folder_name}.txt")

    count = 0
    bag = rosbag.Bag(bag_path, "r")
    for topic, msg, t in bag.read_messages(topics=[image_topic]):
        if topic != image_topic:
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

        with open(timestamp_img_path) as f:
             f.write(f"{t.to_nsec()}\n")

        count += 1
    bag.close()

def save_poses_relative_to_imgs(bag_path, image_folder_name):
    sub_dataset_path = subdataset_path(bag_path)
    timestamp_img_path = os.path.join(sub_dataset_path, f"timestamps_{image_folder_name}.txt")
    timestamp_poses_path = os.path.join(sub_dataset_path, "timestamps_poses.txt")
    poses_path =  os.path.join(sub_dataset_path, "poses.txt")
    interpolate_poses_path = os.path.join(sub_dataset_path, "poses_interp.txt")

    poses = np.loadtxt(poses_path)
    # search timestamps of the images inside poses (poses more frequent)
    poses_interpolated = interpolate_poses(poses, target_timestamps=timestamp_img_path, original_timestamps=timestamp_poses_path)
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


# def interpolate_depth(depth1, depth2, tstamps1, tstamps2, target_tstamp):
#     alpha = (target_tstamp - tstamps1) / (tstamps2 - tstamps1)
#     return alpha * depth1 + (1 - alpha) * depth2

def get_events_from_rosbag(rosbag_path):
    sub_dataset_path = subdataset_path(rosbag_path)
    rosbag_handle = RosbagEventHandle.from_path(rosbag_path)
    events = rosbag_handle.get_between_idx(0, rosbag_handle.num_events[-1])
    h5_path = os.path.join(sub_dataset_path, "events.h5")
    events.to(h5_path)

    return events

# def execute_transformation(dataset, num_events, indices_file_name):
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=None, type=str, help="Current slice to process")
    parser.add_argument("--num_events", default=50000, type=int, help="number of events before the last image")
    parser.add_argument("--indices_file_name", default="indices.txt", type=str, help="name of the file where the indices are stored")
    args=parser.parse_args()