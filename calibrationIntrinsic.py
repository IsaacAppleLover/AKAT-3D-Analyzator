import cv2
import numpy as np
from numpy import load
import glob

def prepare_object_points(chessboard_size, square_size):
    objp = np.zeros((np.prod(chessboard_size), 3), dtype=np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
    objp *= square_size
    return objp

def load_images(path):
    return glob.glob(path)

def find_corners(images, chessboard_size, objp):
    objpoints = []
    imgpoints = []

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                                        criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 80, 0.001))
            imgpoints.append(corners2)
            cv2.drawChessboardCorners(img, chessboard_size, corners2, ret)
            cv2.imshow('Chessboard Corners', img)
            cv2.waitKey()

    cv2.destroyAllWindows()
    return objpoints, imgpoints, gray.shape[::-1]

def calibrate_camera(objpoints, imgpoints, image_shape):
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, image_shape, None, None)
    return ret, mtx, dist, rvecs, tvecs

def save_calibration_parameters(filename, mtx, dist, rvecs, tvecs):
    np.savez(filename, mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

def load_calibration_parameters(filename):
    data = load(filename)
    return {item: data[item] for item in data.files}


def undistort_image(image, mtx, dist):
    h, w = image.shape[:2]
    new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    undistorted_img = cv2.undistort(image, mtx, dist, None, new_camera_mtx)
    x, y, w, h = roi
    undistorted_img = undistorted_img[y:y+h, x:x+w]
    return undistorted_img



def main():
    chessboard_size = (9, 6)
    square_size = 1.0
    objp = prepare_object_points(chessboard_size, square_size)
    images = load_images('Utils/Images/test/Chessboard/links/*.png')
    objpoints, imgpoints, image_shape = find_corners(images, chessboard_size, objp)
    ret, mtx, dist, rvecs, tvecs = calibrate_camera(objpoints, imgpoints, image_shape)
    save_calibration_parameters('intrinsic_calibration_links.npz', mtx, dist, rvecs, tvecs)
    calibration_data = load_calibration_parameters('intrinsic_calibration_links.npz')

    for item, value in calibration_data.items():
        print(item)
        print(value)

    print("Calibration completed and parameters saved.")

if __name__ == "__main__":
    main()
