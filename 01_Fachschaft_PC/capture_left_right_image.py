import threading
import os
import time
from datetime import datetime
from ids_peak import ids_peak, ids_peak_ipl_extension
from ids_peak_ipl import ids_peak_ipl
from ids_peak_afl import ids_peak_afl
from PIL import Image, ImageEnhance
import numpy as np
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import colors


#Laser controller
import serial
ser = serial.Serial('COM3', 9600)
#1ser.open()
ser.flushInput()
laserOn = "1"
laserOn += "\n"
laserOff = "0"
laserOff += "\n"

m_device = None
m_dataStream = None
m_node_map_remote_device = None

devices = []
nodemaps = []
buffers = []
controllers = []
threads = []
data_streams = []


class FinishedCallback(
        ids_peak_afl.FinishedCallback):
    def callback(self) -> None:
        print("ControllerFinishedCallback!")


class ComponentExposureFinishedCallback(
        ids_peak_afl.ComponentExposureFinishedCallback):
    def callback(self) -> None:
        print("ExposureFinishedCallback!")


class ComponentGainFinishedCallback(
        ids_peak_afl.ComponentGainFinishedCallback):
    def callback(self) -> None:
        print("GainFinishedCallback!")

def apply_gamma_correction(image, gamma=0.45):
	inv_gamma = 1.0 / gamma
	table = [((i / 255.0) ** inv_gamma) * 255 for i in range(256)]
	table = np.array(table).astype("uint8")
	return image.point(table)

def increase_brightness(image, factor=2.0):
	enhancer = ImageEnhance.Brightness(image)
	return enhancer.enhance(factor)

def capture_image(remote_nodemap, barrier, m_data_stream, controller, LeftItIs):
	try:
		barrier.wait()
		print(colors.color_text(f"\tStarting acquisition...", colors.COLOR_YELLOW))
		m_data_stream.StartAcquisition()
		remote_nodemap.FindNode("AcquisitionStart").Execute()
		remote_nodemap.FindNode("AcquisitionStart").WaitUntilDone()
		barrier.wait()
		# Get a buffer from the data stream
		buffer = m_data_stream.WaitForFinishedBuffer(5000)
		image = ids_peak_ipl.Image.CreateFromSizeAndBuffer(
			buffer.PixelFormat(),
			buffer.BasePtr(),
			buffer.Size(),
			buffer.Width(),
			buffer.Height()
		)
		rgb_img = image.ConvertTo(ids_peak_ipl.PixelFormatName_BGRa8, ids_peak_ipl.ConversionMode_HighQuality)

		current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
		relative_folder_path = os.path.join("02_Utils", "Images", "capturedImages", current_time)
		os.makedirs(relative_folder_path, exist_ok=True)

		# Entscheidung, ob es sich um ein linkes oder rechtes Bild handelt
		if LeftItIs:
			image_path = os.path.join(relative_folder_path, f"left.bmp")
			print(colors.color_text(f"\tLeft Image Saved", colors.COLOR_YELLOW))
		else:
			image_path = os.path.join(relative_folder_path, f"right.bmp")
			print(colors.color_text(f"\tRight Image Saved", colors.COLOR_YELLOW))
		
		ids_peak_ipl.ImageWriter.Write(image_path, rgb_img)

		# Open image with PIL
		#img = Image.open(image_path)

		# Apply gamma correction
		#img = apply_gamma_correction(img)

		# Increase brightness
		#img = increase_brightness(img)

		# Save the processed image
		#img.save(image_path)

		# Queue the buffer back to the data stream
		m_data_stream.QueueBuffer(buffer)
        
	except Exception as e:
		print(colors.color_text(f"Exception in capture_image: {e}", colors.COLOR_RED))



def main():
	barrier = threading.Barrier(2)
	# Initialize library calls should be matched by a corresponding Exit or close call
	ids_peak.Library.Initialize()
	ids_peak_afl.Library.Init()

	try:

		
		for i in range(2):
			print(colors.color_text(f"\tStarting Camera Number: {i}", colors.COLOR_YELLOW))
			# Create a DeviceManager object
			device_manager = ids_peak.DeviceManager.Instance()
			# Update the DeviceManager
			device_manager.Update()

			# Exit program if no device was found
			if device_manager.Devices().empty():
							print(colors.color_text(f"\tNo device found. Exiting Program.", colors.COLOR_RED))
							return -1
			# Open the first device
			device = device_manager.Devices()[i].OpenDevice(ids_peak.DeviceAccessType_Control)
			print(colors.color_text(f"\tDevice: {device.SerialNumber()} -> {device.DisplayName()}", colors.COLOR_YELLOW))
			# Nodemap for accessing GenICam nodes
			remote_nodemap = device.RemoteDevice().NodeMaps()[0]

			# Autofeature manager, which can have multiple controllers
			manager = ids_peak_afl.Manager(remote_nodemap)
			# Create autofocus controller
			controller = manager.CreateController(
							ids_peak_afl.PEAK_AFL_CONTROLLER_TYPE_BRIGHTNESS)

			print(colors.color_text(f"\tController Status: {controller.Status()}", colors.COLOR_YELLOW))
			print(colors.color_text(f"\tController Type: {controller.Type()}", colors.COLOR_YELLOW))

			# Get frame rate range. All values in fps.
			min_frame_rate = remote_nodemap.FindNode("AcquisitionFrameRate").Minimum()
			max_frame_rate = remote_nodemap.FindNode("AcquisitionFrameRate").Maximum()
			#remote_nodemap.FindNode("AcquisitionFrameRate").SetValue(min_frame_rate)

			remote_nodemap.FindNode("GainSelector").SetCurrentEntry("AnalogAll")

			# Get gain range.
			min_gain = remote_nodemap.FindNode("Gain").Minimum()
			max_gain = remote_nodemap.FindNode("Gain").Maximum()

			#print(f'max_gain = ' + max_gain)

			remote_nodemap.FindNode("Gain").SetValue(max_gain)

			# Manually set exposure time
			exposure_node = remote_nodemap.FindNode("ExposureTime")
			# Get exposure range. All values in microseconds
			min_exposure_time = remote_nodemap.FindNode("ExposureTime").Minimum()
			max_exposure_time = remote_nodemap.FindNode("ExposureTime").Maximum()
			desired_exposure_time = 600  # Example: 1 millisecond
			remote_nodemap.FindNode("ExposureTime").SetValue(desired_exposure_time)
			#exposure_node.SetValue(max_exposure_time)

			# Load default camera settings
			remote_nodemap.FindNode("UserSetSelector").SetCurrentEntry("Default")
			remote_nodemap.FindNode("UserSetLoad").Execute()
			remote_nodemap.FindNode("UserSetLoad").WaitUntilDone()

			# Auto brightness mode is split up in two components
			# so you can't use the regular controller.SetMode etc.
			# NOTE: mode is reset to off automatically after the operation finishes
			# when using PEAK_AFL_CONTROLLER_AUTOMODE_ONCE
			controller.BrightnessComponentSetMode(
							ids_peak_afl.PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_EXPOSURE,
							ids_peak_afl.PEAK_AFL_CONTROLLER_AUTOMODE_ONCE,
			)
			controller.BrightnessComponentSetMode(
							ids_peak_afl.PEAK_AFL_CONTROLLER_BRIGHTNESS_COMPONENT_GAIN,
							ids_peak_afl.PEAK_AFL_CONTROLLER_AUTOMODE_ONCE,
			)

			# Register callbacks
			# NOTE: these have to be assigned, otherwise they get destructed
			# and the callback gets removed
			finished = FinishedCallback(controller)
			exposureFinished = ComponentExposureFinishedCallback(controller)
			gainFinished = ComponentGainFinishedCallback(controller)

			# Open first data stream
			m_data_stream = device.DataStreams()[0].OpenDataStream()
			
			# Buffer size
			payload_size = remote_nodemap.FindNode("PayloadSize").Value()

			# Minimum number of required buffers
			buffer_count_max = m_data_stream.NumBuffersAnnouncedMinRequired()
			# Allocate buffers and add them to the pool
			for buffer_count in range(buffer_count_max):
				# Let the TL allocate the buffers
				buffer = m_data_stream.AllocAndAnnounceBuffer(payload_size)
				# Put the buffer in the pool
				m_data_stream.QueueBuffer(buffer)

			# Lock writeable nodes during acquisition
			remote_nodemap.FindNode("TLParamsLocked").SetValue(1)
   
			#Add variables to array
			devices.append(device)
			nodemaps.append(remote_nodemap)
			buffers.append(buffer)
			controllers.append(controller)
			data_streams.append(m_data_stream)
			LeftItIs = False
			if i == 0:
				LeftItIs = True
			print(colors.color_text(f"\tStarting Thread!", colors.COLOR_YELLOW))
			thread = threading.Thread(target=capture_image, args=(remote_nodemap, barrier, m_data_stream, controller, LeftItIs))
			threads.append(thread)

			# Turn laser on
			if i==1 :
				ser.write(laserOn.encode())

			thread.start()
		# Wait for all threads to finish


		for thread in threads:
			thread.join()

		# Turn laser off
		ser.write(laserOff.encode())

		for i in range(2):
			remote_nodemap = nodemaps[i]
			m_data_stream = data_streams[i]
			buffer = buffers[i]
			controller = controllers[i]
   
			print(colors.color_text(f"\tStopping acquisition...", colors.COLOR_YELLOW))
			remote_nodemap.FindNode("AcquisitionStop").Execute()
			remote_nodemap.FindNode("AcquisitionStop").WaitUntilDone()
			# Remove buffers from any associated queue
			m_data_stream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)

			for buffer in m_data_stream.AnnouncedBuffers():
				# Remove buffer from the transport layer
				m_data_stream.RevokeBuffer(buffer)

			# Unlock writeable nodes again
			remote_nodemap.FindNode("TLParamsLocked").SetValue(0)

			# Last auto average for the controller working on a mono image
			print(f"LastAutoAverage: {controller.GetLastAutoAverage()}")
			
	except Exception as e:
			print(colors.color_text(f"\tEXCEPTION: {e}", colors.COLOR_RED))
			return -2

	finally:
		ids_peak_afl.Library.Exit()
		ids_peak.Library.Close()
  
if __name__ == '__main__':
    main()
