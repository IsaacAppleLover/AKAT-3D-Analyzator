import cv2
import numpy as np
from numpy import load
import glob

# Set the chessboard size and the size of the squares
chessboard_size = (9, 6)
square_size = 1.0  # Sie können dies auf die tatsächliche Größe der Schachbrettquadrate setzen

# Prepare object points
objp = np.zeros((np.prod(chessboard_size), 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size

# Arrays to store object points and image points from all the images
objpoints = []
imgpoints = []

# Load all images using glob
images = glob.glob('Utils/Images/test/Chessboard/links/*.png')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    # If found, add object points, image points (after refining them)
    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                                    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 80, 0.001))
        imgpoints.append(corners2)

        # Draw and display the corners
        cv2.drawChessboardCorners(img, chessboard_size, corners2, ret)
        cv2.imshow('Chessboard Corners', img)
        cv2.waitKey()  # Show each image for 500 ms
#cv2.destroyAllWindows()

# Calibrate the camera
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Save the calibration result for later use
np.savez('camera_calibration_links.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

data = load('camera_calibration_links.npz')
lst = data.files
for item in lst:
    print(item)
    print(data[item])


print("Calibration completed and parameters saved.")


