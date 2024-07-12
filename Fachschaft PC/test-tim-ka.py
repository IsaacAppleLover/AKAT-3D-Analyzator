import cv2
from ids_peak import ids_peak

# Initialize the IDS peak library
ids_peak.Library.Initialize()

# Open the first available camera device
device_manager = ids_peak.DeviceManager.Instance()
if device_manager.Devices().empty():
    print("No device found. Exiting program.")
    exit(-1)
device = device_manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Control)

# Open a data stream and allocate buffers
data_stream = device.DataStreams()[0].OpenDataStream()
payload_size = device.RemoteDevice().NodeMaps()[0].FindNode("PayloadSize").Value()
buffer_count_max = data_stream.NumBuffersAnnouncedMinRequired()

for buffer_count in range(buffer_count_max):
    buffer = data_stream.AllocAndAnnounceBuffer(payload_size)
    data_stream.QueueBuffer(buffer)

# Start image acquisition
device.RemoteDevice().NodeMaps()[0].FindNode("TLParamsLocked").SetValue(1)
print("Starting acquisition...")
data_stream.StartAcquisition()
device.RemoteDevice().NodeMaps()[0].FindNode("AcquisitionStart").Execute()
device.RemoteDevice().NodeMaps()[0].FindNode("AcquisitionStart").WaitUntilDone()

try:
    while True:
        # Retrieve a frame
        buffer = data_stream.WaitForFinishedBuffer(5000)
        if buffer:
            frame_data = buffer.Data()
            frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
            cv2.imshow("Live Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
finally:
    # Clean up
    data_stream.StopAcquisition()
    cv2.destroyAllWindows()
    device.CloseDevice()
    ids_peak.Library.Close()
