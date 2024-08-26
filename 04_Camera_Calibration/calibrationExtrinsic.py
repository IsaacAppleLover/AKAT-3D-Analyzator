import cv2
import numpy as np
import glob

# Set the chessboard size and square size
chessboard_size = (7, 6)
square_size = 1.0  # Set this to the actual size of the chessboard squares

# Prepare object points
objp = np.zeros((np.prod(chessboard_size), 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size

# Arrays to store object points and image points from all the images
objpoints = []  # 3D points in real world space
imgpoints_left = []  # 2D points in image plane for left camera
imgpoints_right = []  # 2D points in image plane for right camera

# Load all image pairs
images_left = glob.glob('02_Utils/Images/02_Chessboard/01_links/*.png')
images_right = glob.glob('02_Utils/Images/02_Chessboard/01_rechts/*.png')

# Make sure the number of images match
assert len(images_left) == len(images_right), "The number of left and right images must be the same"

for img_left, img_right in zip(images_left, images_right):
    imgL = cv2.imread(img_left)
    imgR = cv2.imread(img_right)
    grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
    grayR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    retL, cornersL = cv2.findChessboardCorners(grayL, chessboard_size, None)
    retR, cornersR = cv2.findChessboardCorners(grayR, chessboard_size, None)

    # If found, add object points, image points (after refining them)
    if retL and retR:
        objpoints.append(objp)

        cornersL2 = cv2.cornerSubPix(grayL, cornersL, (11, 11), (-1, -1),
                                     criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        imgpoints_left.append(cornersL2)

        cornersR2 = cv2.cornerSubPix(grayR, cornersR, (11, 11), (-1, -1),
                                     criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        imgpoints_right.append(cornersR2)

        # Draw and display the corners
        cv2.drawChessboardCorners(imgL, chessboard_size, cornersL2, retL)
        cv2.drawChessboardCorners(imgR, chessboard_size, cornersR2, retR)
        cv2.imshow('Corners Left', imgL)
        cv2.imshow('Corners Right', imgR)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# Load the intrinsic parameters of both cameras
with np.load('calibration_data_left.npz') as data:
    camera_matrix_1 = data['camera_matrix']
    dist_coeffs_1 = data['distortion_coeffs']

with np.load('calibration_data_right.npz') as data:
    camera_matrix_2 = data['camera_matrix']
    dist_coeffs_2 = data['distortion_coeffs']

# Stereo calibration
ret, camera_matrix_1, dist_coeffs_1, camera_matrix_2, dist_coeffs_2, R, T, E, F = cv2.stereoCalibrate(
    objpoints, imgpoints_left, imgpoints_right,
    camera_matrix_1, dist_coeffs_1,
    camera_matrix_2, dist_coeffs_2,
    grayL.shape[::-1], criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6),
    flags=cv2.CALIB_FIX_INTRINSIC)

# Save the stereo calibration result
np.savez('stereo_calibration.npz', camera_matrix_1=camera_matrix_1, dist_coeffs_1=dist_coeffs_1,
         camera_matrix_2=camera_matrix_2, dist_coeffs_2=dist_coeffs_2, R=R, T=T, E=E, F=F)

print("Stereo calibration completed and parameters saved.")
print("Rotation Matrix:\n", R)
print("Translation Vector:\n", T)

# Rectify the stereo pair
R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(
    camera_matrix_1, dist_coeffs_1, camera_matrix_2, dist_coeffs_2,
    grayL.shape[::-1], R, T, alpha=0)

# Save rectification parameters
np.savez('stereo_rectification.npz', R1=R1, R2=R2, P1=P1, P2=P2, Q=Q, validPixROI1=validPixROI1, validPixROI2=validPixROI2)
