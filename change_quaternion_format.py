import numpy as np
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

from evo.core import sync
from evo.tools import plot
import evo.main_ape as main_ape
from evo.core.metrics import PoseRelation
from evo.core.trajectory import PoseTrajectory3D

def quaternion_rotate_xz_only(quaternion):
    # Create a Rotation object from the quaternion
    r = R.from_quat(quaternion)
    
    # Convert the rotation to Euler angles (in radians)
    euler = r.as_euler('xyz')  # Get Euler angles (x, y, z)
    
    # Set the rotation around the y axis to zero
    euler[1] = 0  # Set rotation around y to zero
    
    # Create a new Rotation object from Euler angles
    r_new = R.from_euler('xyz', euler)
    
    # Convert the new rotation to quaternion
    new_quaternion = r_new.as_quat()
    
    return new_quaternion

def change_quaternion_format(quat):
    """Change quaternion format from [x, y, z, w] to [w, x, y, z]"""
    quat = np.roll(quat, 1, axis=1)  # shift 1 column -> w in front column
    return quat

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quaternion format [x, y, z, w]")
    parser.add_argument("--traj_path", help="Quaternion to change format")
    parser.add_argument("--output_path", help="Output path")
    parser.add_argument("--wxyz", help="Output path", action="store_true")
    parser.add_argument("--w_to_one", help="Output path", action="store_true")
    args = parser.parse_args()

    if args.wxyz:
        trajectory = np.loadtxt(args.traj_path)
        trajectory_ = trajectory[:, (0,1,2,3, 7,4,5,6)]
        with open(args.output_path, "w") as f:
            np.savetxt(f, trajectory_)
    
    if args.w_to_one:
        trajectory = np.loadtxt(args.traj_path)
        for pose in trajectory:
            new_quaternion = quaternion_rotate_xz_only(pose[4:])
            pose[4:] = new_quaternion

        with open(args.output_path, "w") as f:
            np.savetxt(f, trajectory)
