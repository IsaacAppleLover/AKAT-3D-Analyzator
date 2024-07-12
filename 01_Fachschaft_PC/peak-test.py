from ids_peak import ids_peak, ids_peak_ipl_extension
from ids_peak_ipl import ids_peak_ipl
from ids_peak_afl import ids_peak_afl
from PIL import Image
import sys

m_device = None
m_dataStream = None
m_node_map_remote_device = None


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


def main():
    # Initialize library calls should be matched by a corresponding
    # Exit or close call
    ids_peak.Library.Initialize()
    ids_peak_afl.Library.Init()

    # Create a DeviceManager object
    device_manager = ids_peak.DeviceManager.Instance()

    try:
        # Update the DeviceManager
        device_manager.Update()

        # Exit program if no device was found
        if device_manager.Devices().empty():
            print("No device found. Exiting Program.")
            return -1

        # Open the first device
        device = device_manager.Devices()[0].OpenDevice(
            ids_peak.DeviceAccessType_Control)

        print(f"Device: {device.SerialNumber()} -> {device.DisplayName()}")

        # Nodemap for accessing GenICam nodes
        remote_nodemap = device.RemoteDevice().NodeMaps()[0]

        # Autofeature manager, which can have multiple controllers
        manager = ids_peak_afl.Manager(remote_nodemap)
        # Create autofocus controller
        controller = manager.CreateController(
            ids_peak_afl.PEAK_AFL_CONTROLLER_TYPE_BRIGHTNESS)

        print(f"Controller Status: {controller.Status()}")
        print(f"Controller Type: {controller.Type()}")

        # Get frame rate range. All values in fps.
        min_frame_rate = remote_nodemap.FindNode("AcquisitionFrameRate").Minimum()
        max_frame_rate = remote_nodemap.FindNode("AcquisitionFrameRate").Maximum()
        remote_nodemap.FindNode("AcquisitionFrameRate").SetValue(min_frame_rate)

        remote_nodemap.FindNode("GainSelector").SetCurrentEntry("AnalogAll")

         # Get gain range.
        min_gain = remote_nodemap.FindNode("Gain").Minimum()
        max_gain = remote_nodemap.FindNode("Gain").Maximum()

        remote_nodemap.FindNode("Gain").SetValue(max_gain)

        # Manually set exposure time
        exposure_node = remote_nodemap.FindNode("ExposureTime")  # Replace with actual node name
        # Get exposure range. All values in microseconds
        min_exposure_time = remote_nodemap.FindNode("ExposureTime").Minimum()
        max_exposure_time = remote_nodemap.FindNode("ExposureTime").Maximum()
        desired_exposure_time = 600  # Example: 1 millisecond
        exposure_node.SetValue(max_exposure_time)

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

        print("Starting acquisition...")
        m_data_stream.StartAcquisition()
        remote_nodemap.FindNode("AcquisitionStart").Execute()
        remote_nodemap.FindNode("AcquisitionStart").WaitUntilDone()

        print("Getting 1 images...")
        # Process 100 images
        for _ in range(1):
            try:
                buffer = m_data_stream.WaitForFinishedBuffer(5000)

                image = ids_peak_ipl.Image.CreateFromSizeAndBuffer(
                    buffer.PixelFormat(),
                    buffer.BasePtr(),
                    buffer.Size(),
                    buffer.Width(),
                    buffer.Height()
                )
                rgb_img = image.ConvertTo(ids_peak_ipl.PixelFormatName_BGRa8, ids_peak_ipl.ConversionMode_Fast)
                image_path = "C:\\Users\\Administrator\\Desktop\\KAT\\Output\\new\\"+"99.png"
                ids_peak_ipl.ImageWriter.Write(image_path, rgb_img)
                m_data_stream.QueueBuffer(buffer)
            except Exception as e:
                print(f"Exception: {e}")

        print("Stopping acquisition...")
        remote_nodemap.FindNode("AcquisitionStop").Execute()
        remote_nodemap.FindNode("AcquisitionStop").WaitUntilDone()

        m_data_stream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)

        # In case another thread is waiting on WaitForFinishedBuffer
        # you can interrupt it using:
        # data_stream.KillWait()

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
        print(f"EXCEPTION: {e}")
        return -2

    finally:
        ids_peak_afl.Library.Exit()
        ids_peak.Library.Close()


if __name__ == '__main__':
    main()