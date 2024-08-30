import time
from pyueye import ueye
import threading

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