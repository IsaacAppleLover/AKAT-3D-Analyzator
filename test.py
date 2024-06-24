import time
from pyueye import ueye
import threading
import numpy as np
import cv2

def capture_image(cam_handle, filename, barrier):
    # Get the image size
    rectAOI = ueye.IS_RECT()
    ueye.is_AOI(cam_handle, ueye.IS_AOI_IMAGE_GET_AOI, rectAOI, ueye.sizeof(rectAOI))
    width = rectAOI.s32Width
    height = rectAOI.s32Height

    # Allocate memory for the image
    mem_ptr = ueye.c_mem_p()
    mem_id = ueye.int()
    bitspixel = 8
    ret = ueye.is_AllocImageMem(cam_handle, width, height, bitspixel, mem_ptr, mem_id)
    if ret != ueye.IS_SUCCESS:
        print(f"Error allocating image memory: {ret}")
        return
    ret = ueye.is_SetImageMem(cam_handle, mem_ptr, mem_id)
    if ret != ueye.IS_SUCCESS:
        print(f"Error setting image memory: {ret}")
        return
    barrier.wait()
    # Capture a single image
    result = ueye.is_FreezeVideo(cam_handle, ueye.IS_WAIT)
    if result != ueye.IS_SUCCESS:
        print(f"Error freezing video: {result}")
        return

    # Save the image with a timestamp
    img_file_params = ueye.IMAGE_FILE_PARAMS()
    img_file_params.pwchFileName = filename
    img_file_params.nFileType = ueye.IS_IMG_BMP
    img_file_params.ppcImageMem = None
    img_file_params.pnImageID = None
    result = ueye.is_ImageFile(cam_handle, ueye.IS_IMAGE_FILE_CMD_SAVE, img_file_params, ueye.sizeof(img_file_params))
    if result != ueye.IS_SUCCESS:
        print(f"Error saving image: {result}")

    # Free the allocated image memory
    ueye.is_FreeImageMem(cam_handle, mem_ptr, mem_id)

def calibrate_camera(chessboard_size, image_paths):

    # Prepare object points, like (0,0,0), (1,0,0), ..., (8,5,0)
    object_points = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    object_points[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images
    object_points_list = []  # 3D points in real world space
    image_points_list = []  # 2D points in image plane

    # Load the images
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
            cv2.imshow('Chessboard Corners', image)
            cv2.waitKey(0)

    # Calibrate the camera,  function returns the camera matrix, distortion coefficients, rotation and translation vectors etc.
    ret, camera_matrix, distortion_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        object_points_list, image_points_list, gray.shape[::-1], None, None)
    
    np.savez("calibration_data.npz", camera_matrix=camera_matrix, distortion_coeffs=distortion_coeffs, rvecs=rvecs, tvecs=tvecs)

    # Print the camera matrix and distortion coefficients
    print("Camera Matrix:")
    print(camera_matrix)
    print("\nDistortion Coefficients:")
    print(distortion_coeffs)
    print("\nRotation Vectors:")
    print(rvecs)
    print("\nTranslation Vectors:")
    print(tvecs)

def undistort_image(camera_matrix, distortion_coeffs, image_path):
    # Load the distorted image and refine camera matrix
    distorted_image = cv2.imread(image_path)
    h, w = distorted_image.shape[:2]
    newcamera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coeffs, (w, h), 1, (w, h))

    # Undistort the image
    undistorted_image = cv2.undistort(distorted_image, camera_matrix, distortion_coeffs, None, newcamera_matrix)

    # Crop the image
    x, y, w, h = roi
    undistorted_image = undistorted_image[y:y+h, x:x+w]

    return undistorted_image

def reprojection_error(object_points_list, image_points_list, rvecs, tvecs, camera_matrix, distortion_coeffs):
    total_error = 0
    for i in range(len(object_points_list)):
        image_points, _ = cv2.projectPoints(object_points_list[i], rvecs[i], tvecs[i], camera_matrix, distortion_coeffs)
        error = cv2.norm(image_points_list[i], image_points, cv2.NORM_L2) / len(image_points)
        total_error += error
    return total_error / len(object_points_list)


def main():
    barrier = threading.Barrier(2)
    # Get the number of connected cameras
    num_cameras = ueye.INT()
    result = ueye.is_GetNumberOfCameras(num_cameras)
    print(num_cameras.value)
    if result != ueye.IS_SUCCESS:
        print(f"Error getting number of cameras: {result}")
        return
    threads = []
    cam_handles = []

    for i in range(2):  # For left and right cameras
        # Create a camera handle
        cam_handle = ueye.HIDS(i)
        cam_handles.append(cam_handle)
        # Open the camera
        result = ueye.is_InitCamera(cam_handle, None)
        if result != ueye.IS_SUCCESS:
            print(f"Error initializing camera {i}: {result}")
            continue

        # Set the color mode to 8-bit monochrome
        result = ueye.is_SetColorMode(cam_handle, ueye.IS_CM_MONO8)
        if result != ueye.IS_SUCCESS:
            print(f"Error setting color mode for camera {i}: {result}")
            continue

        # Capture an image
        filename = f"C:\\Users\\Administrator\\Desktop\\KAT\\Output\\image_{time.time()}_{'left' if i == 0 else 'right'}.bmp"
        thread = threading.Thread(target=capture_image, args=(cam_handle, filename, barrier))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Close the cameras
    for cam_handle in cam_handles:
        ueye.is_ExitCamera(cam_handle)

if __name__ == "__main__":
    main()