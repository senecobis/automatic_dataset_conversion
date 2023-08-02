import cv2
import numpy as np
import os

# Define the size of the squares on the checkerboard (in meters)
square_size = 1  # Adjust this value according to the actual size of the squares

# Known distances from the camera to the checkerboard (in meters)
known_distances = [22,22,28,28,28]

# Arrays to store detected image points and corresponding 3D world points
image_points = []
world_points = []

# Define the checkerboard pattern size (number of inner corners)
pattern_size = (9, 9) 

image_paths = ["checkboard_images/0.png", "checkboard_images/1.png", "checkboard_images/2.png", "checkboard_images/3.png",  "checkboard_images/4.png", ]

# Loop through each image
for image_path in image_paths:  # Replace image_paths with a list of paths to your checkerboard images
    image = cv2.imread(os.path.join("/home/pellerito/Automatic_dataset_conversion", image_path))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Find checkerboard corners
    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)

    # If corners are found, add image points and corresponding world points
    if ret:
        image_points.append(corners)
        world_points.append(np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32))
        world_points[-1][:, :2] = square_size * np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)

# Camera calibration
ret, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(world_points, image_points, gray.shape[::-1], None, None)

# Extract intrinsic parameters from the camera matrix
focal_length_x = camera_matrix[0, 0]
focal_length_y = camera_matrix[1, 1]
central_point_x = camera_matrix[0, 2]
central_point_y = camera_matrix[1, 2]

print("Focal Length (x):", focal_length_x)
print("Focal Length (y):", focal_length_y)
print("Central Point (x):", central_point_x)
print("Central Point (y):", central_point_y)