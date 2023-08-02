import numpy as np

# Load data from the text file
data = np.loadtxt("/data/storage/pellerito/MoonLanding/Malapert_crater/Cam1/pose_left_old.txt")

# Rearrange the columns
rearranged_data = data[:, [0, 1, 2, 4, 5, 6, 3]]

# Save the updated data to a new text file
np.savetxt("/data/storage/pellerito/MoonLanding/Malapert_crater/Cam1/pose_left_mod.txt", rearranged_data, delimiter=' ')
