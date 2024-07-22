import numpy as np

path = "/home/pellerito/DPVO/trajectory_evaluation/Merger_LSTM/-full_data/trial_0/03_rocket_earth_dark_0-100"

stamped_groundtruth = np.loadtxt(f"{path}/stamped_groundtruth.txt")
stamped_groundtruth = stamped_groundtruth[::10]
np.savetxt(f"{path}/stamped_groundtruth.txt", stamped_groundtruth)

stamped_traj_estimate = np.loadtxt(f"{path}/stamped_traj_estimate.txt")
stamped_traj_estimate = stamped_traj_estimate[::10]
np.savetxt(f"{path}/stamped_traj_estimate.txt", stamped_traj_estimate)
