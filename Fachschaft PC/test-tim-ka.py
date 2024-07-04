from ids_peak import ids_peak, ids_peak_ipl_extension
from ids_peak_ipl import ids_peak_ipl
from ids_peak_afl import ids_peak_afl
from PIL import Image
import sys

import cv2
import numpy as np


def init_camera(camera_index):
    # Initialize the system
    system = ids_peak.Library.Initialize()
    device_manager = system.CreateDeviceManager()
    device_manager.Update()
    devices = device_manager.Devices()

    # Open the camera device
    camera = devices[camera_index].OpenDevice(ids_peak.DeviceAccessType.Control)
    node_map = camera.NodeMaps[0]

    # Set acquisition mode to continuous
    node_map.FindNode("AcquisitionMode").Value = "Continuous"

    # Set pixel format to BGR8
    node_map.FindNode("PixelFormat").Value = "BGR8"

    # Allocate buffer and start acquisition
    data_stream = camera.DataStreams[0]
    data_stream.StartAcquisition()

    return camera, data_stream

def capture_image(data_stream):
    buffer = data_stream.WaitForFinishedBuffer(5000)  # Wait for 5 seconds to capture the image
    if buffer is not None:
        image_data = buffer.GetImage()
        image = np.frombuffer(image_data, dtype=np.uint8).reshape(image_data.Height(), image_data.Width(), 3)
        buffer.QueueBuffer()
        return image
    else:
        return None

def main():
    # Initialize both cameras
    cam1, data_stream1 = init_camera(0)
    cam2, data_stream2 = init_camera(1)

    # Capture images from both cameras
    img1 = capture_image(data_stream1)
    img2 = capture_image(data_stream2)

    if img1 is not None:
        cv2.imshow('Camera 1', img1)
    else:
        print("Failed to capture image from Camera 1")

    if img2 is not None:
        cv2.imshow('Camera 2', img2)
    else:
        print("Failed to capture image from Camera 2")

    cv2.waitKey(0)

    # Stop acquisition and close cameras
    data_stream1.StopAcquisition()
    data_stream2.StopAcquisition()
    cam1.Close()
    cam2.Close()
    ids_peak.Library.Close()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()