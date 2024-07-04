import os
from ids_peak import ids_peak, ids_peak_ipl_extension, EnumCameraList
from ids_peak_ipl import ids_peak_ipl
from ids_peak_afl import ids_peak_afl

def capture_and_save(icam, file_name):
  """Captures an image from the specified camera and saves it locally.

  Args:
    icam: An instance of the IDS peak camera object.
    file_name: The name of the file to save the image to.
  """
  # Start image acquisition
  ret = icam.AcquisitionStart()
  if ret != ids_peak.PICAM_ACQUISITION_START_SUCCESS:
    print(f"Error: Failed to start acquisition. Error code: {ret}")
    return

  # Capture image
  image = icam.GetImage()
  if image is None:
    print("Error: Failed to capture image.")
    return

  # Save image
  os.makedirs(os.path.dirname(file_name), exist_ok=True)  # Create directory if it doesn't exist
  ret = image.Save(file_name, ids_peak_ipl.IPL_FILE_FORMAT_JPEGL)
  if ret != ids_peak_ipl.IPL_SUCCESS:
    print(f"Error: Failed to save image. Error code: {ret}")
  image.Release()

  # Stop acquisition
  ret = icam.AcquisitionStop()
  if ret != ids_peak.PICAM_ACQUISITION_STOP_SUCCESS:
    print(f"Error: Failed to stop acquisition. Error code: {ret}")

# Initialize camera objects
# Enumerate available cameras
camera_list = ids_peak.EnumCameraList()
ret = camera_list.EnumerateCameras()
if ret != ids_peak.PICAM_SUCCESS:
  print(f"Error: Failed to enumerate cameras. Error code: {ret}")
  exit(1)

num_cameras = len(camera_list)

cameras = []
for i in range(ids_peak.PI_CAMERA_COUNT):
  icam = ids_peak.ids_peak()
  ret = icam.OpenDevice(i)
  if ret != ids_peak.PICAM_OPEN_SUCCESS:
    print(f"Error: Failed to open camera {i}. Error code: {ret}")
    continue
  cameras.append(icam)

# Check if at least two cameras are opened
if len(cameras) < 2:
  print("Error: Not enough cameras found. Please connect at least two cameras.")
  for cam in cameras:
    cam.CloseDevice()
  exit(1)

# Capture images from both cameras with unique filenames
for i, cam in enumerate(cameras):
  file_name = f"camera_{i+1}.jpg"
  capture_and_save(cam, file_name)

# Close cameras
for cam in cameras:
  cam.CloseDevice()

print("Images captured and saved successfully!")
