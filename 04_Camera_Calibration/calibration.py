import cv2
import numpy as np

chessboard_size = (7, 6)

# Prepare object points, like (0,0,0), (1,0,0), ..., (8,5,0)
object_points = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
object_points[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images
object_points_list = []  # 3D points in real world space
image_points_list = []  # 2D points in image plane

# Load the images
image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']  # We need 10 images
for image_path in image_paths:
    # Read the image
    image = cv2.imread(image_path)
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Find the chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
    
    # If corners are found, add object points and image points
    if ret == True:
        object_points_list.append(object_points)

        # cv.cornerSubPix is used to refine the corner locations
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        image_points_list.append(corners2)
        
        # Draw and display the corners
        cv2.drawChessboardCorners(image, chessboard_size, corners2, ret)
        cv2.imshow('02_Chessboard Corners', image)
        cv2.waitKey(0)

# Calibrate the camera,  function returns the camera matrix, distortion coefficients, rotation and translation vectors etc.
ret, camera_matrix, distortion_coeffs, rvecs, tvecs = cv2.calibrateCamera(
    object_points_list, image_points_list, gray.shape[::-1], None, None)

# Print the camera matrix and distortion coefficients
print("Camera Matrix:")
print(camera_matrix)
print("\nDistortion Coefficients:")
print(distortion_coeffs)
print("\nRotation Vectors:")
print(rvecs)
print("\nTranslation Vectors:")
print(tvecs)

# Undistort the images
# Load the distorted image and refine camera matrix
distorted_image = cv2.imread('distorted_image.jpg')
h, w = distorted_image.shape[:2]
newcamera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coeffs, (w, h), 1, (w, h))



# Undistort the image
undistorted_image = cv2.undistort(distorted_image, camera_matrix, distortion_coeffs, None, newcamera_matrix)

# Crop the image
x, y, w, h = roi
undistorted_image = undistorted_image[y:y+h, x:x+w]
cv2.imwrite('calibresult.png', undistorted_image)

# Display the undistorted image
cv2.imshow('Undistorted Image', undistorted_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Store matrix, distortion coefficients, rotation and translation vectors
np.savez('calibration_data.npz', camera_matrix=camera_matrix, distortion_coeffs=distortion_coeffs, rvecs=rvecs, tvecs=tvecs)

# Re-projection error
mean_error = 0
for i in range(len(object_points_list)):
    image_points, _ = cv2.projectPoints(object_points_list[i], rvecs[i], tvecs[i], camera_matrix, distortion_coeffs)
    error = cv2.norm(image_points_list[i], image_points, cv2.NORM_L2) / len(image_points)
    mean_error += error

print("Total error: ", mean_error / len(object_points_list))