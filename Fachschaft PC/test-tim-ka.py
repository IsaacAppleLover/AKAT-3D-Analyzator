from ids_peak import ids_peak, ids_peak_ipl_extension
from ids_peak_ipl import ids_peak_ipl
from ids_peak_afl import ids_peak_afl
from PIL import Image, ImageEnhance
import numpy as np

m_device = None
m_data_stream = None
m_node_map_remote_device = None

class FinishedCallback(ids_peak_afl.FinishedCallback):
    def callback(self) -> None:
        print("ControllerFinishedCallback!")

class ComponentExposureFinishedCallback(ids_peak_afl.ComponentExposureFinishedCallback):
    def callback(self) -> None:
        print("ExposureFinishedCallback!")

class ComponentGainFinishedCallback(ids_peak_afl.ComponentGainFinishedCallback):
    def callback(self) -> None:
        print("GainFinishedCallback!")

def apply_gamma_correction(image, gamma=0.45):
    inv_gamma = 1.0 / gamma
    table = [((i / 255.0) ** inv_gamma) * 255 for i in range(256)]
    table = np.array(table).astype("uint8")
    return Image.fromarray(np.asarray(image.point(table)))

def increase_brightness(image, factor=2.0):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

def main():
    # Initialize library calls should be matched by a corresponding Exit or close call
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
        device = device_manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Control)

        print(f"Device: {device.SerialNumber()} -> {device.DisplayName()}")

        # Nodemap for accessing GenICam nodes
        remote_nodemap = device.RemoteDevice().NodeMaps()[0]

        # Autofeature manager, which can have multiple controllers
        manager = ids_peak_afl.Manager(remote_nodemap)
        # Create autofocus controller
        controller = manager.CreateController(ids_peak_afl.PEAK_AFL_CONTROLLER_TYPE_BRIGHTNESS)

        print(f"Controller Status: {controller.Status()}")
        print(f"Controller Type: {controller.Type()}")

        # Enable auto exposure and auto gain
        remote_nodemap.FindNode("ExposureAuto").SetCurrentEntry("Continuous")
        remote_nodemap.FindNode("GainAuto").SetCurrentEntry("Continuous")

        # Load default camera settings
        remote_nodemap.FindNode("UserSetSelector").SetCurrentEntry("Default")
        remote_nodemap.FindNode("UserSetLoad").Execute()
        remote_nodemap.FindNode("UserSetLoad").WaitUntilDone()

        # Register callbacks
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
            buffer = m_data_stream.AllocAndAnnounceBuffer(payload_size)
            m_data_stream.QueueBuffer(buffer)

        # Lock writeable nodes during acquisition
        remote_nodemap.FindNode("TLParamsLocked").SetValue(1)

        print("Starting acquisition...")
        m_data_stream.StartAcquisition()
        remote_nodemap.FindNode("AcquisitionStart").Execute()
        remote_nodemap.FindNode("AcquisitionStart").WaitUntilDone()

        print("Getting 1 image...")
        for _ in range(1):
            try:
                buffer = m_data_stream.WaitForFinishedBuffer('INFINITE_NUMBER')

                image = ids_peak_ipl.Image.CreateFromSizeAndBuffer(
                    buffer.PixelFormat(),
                    buffer.BasePtr(),
                    buffer.Size(),
                    buffer.Width(),
                    buffer.Height()
                )
                rgb_img = image.ConvertTo(ids_peak_ipl.PixelFormatName_BGRa8, ids_peak_ipl.ConversionMode_Fast)
                image_path = "C:\\Users\\Administrator\\Desktop\\KAT\\Output\\new\\tim3.png"
                ids_peak_ipl.ImageWriter.Write(image_path, rgb_img)
                
                # Open image with PIL
                img = Image.open(image_path)
                
                # Apply gamma correction
                img = apply_gamma_correction(img)
                
                # Increase brightness
                img = increase_brightness(img)
                
                # Increase brightness of each pixel by 100
                img = img.point(lambda p: p + 100)
                
                # Save the processed image
                img.save(image_path)
                
                m_data_stream.QueueBuffer(buffer)
            except Exception as e:
                print(f"Exception: {e}")

        print("Stopping acquisition...")
        remote_nodemap.FindNode("AcquisitionStop").Execute()
        remote_nodemap.FindNode("AcquisitionStop").WaitUntilDone()

        m_data_stream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)

        # Remove buffers from any associated queue
        m_data_stream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)

        for buffer in m_data_stream.AnnouncedBuffers():
            m_data_stream.RevokeBuffer(buffer)

        # Unlock writeable nodes again
        remote_nodemap.FindNode("TLParamsLocked").SetValue(0)

        print(f"LastAutoAverage: {controller.GetLastAutoAverage()}")

    except Exception as e:
        print(f"EXCEPTION: {e}")
        return -2

    finally:
        ids_peak_afl.Library.Exit()
        ids_peak.Library.Close()

if __name__ == '__main__':
    main()