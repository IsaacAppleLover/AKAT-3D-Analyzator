from ids_peak import ids_peak, ids_peak_ipl_extension
from ids_peak_ipl import ids_peak_ipl
from ids_peak_afl import ids_peak_afl
import threading

class CamThread(threading.Thread):
    def __init__(self, previewName, device_serial):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.device_serial = device_serial

    def run(self):
        print(f"Starting {self.previewName}")
        camPreview(self.previewName, self.device_serial)

def camPreview(previewName, device_serial):
    # Initialize library calls should be matched by a corresponding Exit or close call
    ids_peak.Library.Initialize()
    ids_peak_afl.Library.Init()

    # Create a DeviceManager object
    device_manager = ids_peak.DeviceManager.Instance()

    try:
        # Update the DeviceManager
        device_manager.Update()

        # Find the device with the specified serial number
        device = None
        for dev in device_manager.Devices():
            if dev.SerialNumber() == device_serial:
                device = dev
                break

        if not device:
            print(f"Device with serial number {device_serial} not found.")
            return

        # Open the device
        device.OpenDevice(ids_peak.DeviceAccessType_Control)

        # Nodemap for accessing GenICam nodes
        remote_nodemap = device.RemoteDevice().NodeMaps()[0]

        # Set camera settings (e.g., exposure, gain, etc.) as needed
        # ...

        # Start image acquisition
        data_stream = device.DataStreams()[0].OpenDataStream()
        data_stream.StartAcquisition()

        while True:
            try:
                buffer = data_stream.WaitForFinishedBuffer(1000)
                img = ids_peak_ipl_extension.BufferToImage(buffer)
                # Process the image (e.g., save, display, etc.)
                # ...

                data_stream.QueueBuffer(buffer)
            except Exception as e:
                print(f"Exception: {e}")
                break

        data_stream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)
        data_stream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)

    except Exception as e:
        print(f"EXCEPTION: {e}")

    finally:
        ids_peak_afl.Library.Exit()
        ids_peak.Library.Close()

if __name__ == '__main__':
    thread1 = CamThread("Camera 1", "4108763732")
    thread2 = CamThread("Camera 2", "4108763731")

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
