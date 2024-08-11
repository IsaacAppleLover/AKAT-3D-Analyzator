import sys
from PySide6.QtWidgets import QVBoxLayout, QWidget, QApplication, QMessageBox
from PySide6.QtCore import QTimer, Slot
from PySide6.QtGui import QImage
from ids_peak import ids_peak
from ids_peak_ipl import ids_peak_ipl
from ids_peak import ids_peak_ipl_extension
from components.display import Display  # Korrekt importieren

FPS_LIMIT = 30
TARGET_PIXEL_FORMAT = ids_peak_ipl.PixelFormatName_BGRa8

class BigWindow_Live(QWidget):
    def __init__(self):
        super().__init__()
        self.__device = None
        self.__nodemap_remote_device = None
        self.__datastream = None
        self.__acquisition_timer = QTimer()
        self.__acquisition_running = False
        self.__image_converter = ids_peak_ipl.ImageConverter()

        self.initUI()

        ids_peak.Library.Initialize()

        if self.__open_device():
            self.__start_acquisition()
        else:
            self.__destroy_all()
            sys.exit(0)

        self.setMinimumSize(700, 500)

    def initUI(self):
        a = QApplication(sys.argv)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.display = Display(self)  # Erstelle eine Instanz von Display
        layout.addWidget(self.display)  # Füge das Display-Widget zum Layout hinzu

        self.setLayout(layout)
        self.setWindowTitle('BigWindow Live')
        self.show()

    def __del__(self):
        self.__destroy_all()

    def __destroy_all(self):
        self.__stop_acquisition()
        self.__close_device()
        ids_peak.Library.Close()

    def __open_device(self):
        try:
            device_manager = ids_peak.DeviceManager.Instance()
            device_manager.Update()

            if device_manager.Devices().empty():
                return False

            for device in device_manager.Devices():
                if device.IsOpenable():
                    self.__device = device.OpenDevice(ids_peak.DeviceAccessType_Control)
                    break

            if self.__device is None:
                return False

            datastreams = self.__device.DataStreams()
            if datastreams.empty():
                self.__device = None
                return False

            self.__datastream = datastreams[0].OpenDataStream()
            self.__nodemap_remote_device = self.__device.RemoteDevice().NodeMaps()[0]

            try:
                self.__nodemap_remote_device.FindNode("UserSetSelector").SetCurrentEntry("Default")
                self.__nodemap_remote_device.FindNode("UserSetLoad").Execute()
                self.__nodemap_remote_device.FindNode("UserSetLoad").WaitUntilDone()
            except ids_peak.Exception:
                pass

            payload_size = self.__nodemap_remote_device.FindNode("PayloadSize").Value()
            buffer_count_max = self.__datastream.NumBuffersAnnouncedMinRequired()

            for i in range(buffer_count_max):
                buffer = self.__datastream.AllocAndAnnounceBuffer(payload_size)
                self.__datastream.QueueBuffer(buffer)

            return True
        except ids_peak.Exception:
            return False

    def __close_device(self):
        self.__stop_acquisition()
        if self.__datastream is not None:
            try:
                for buffer in self.__datastream.AnnouncedBuffers():
                    self.__datastream.RevokeBuffer(buffer)
            except Exception:
                pass

    def __start_acquisition(self):
        if self.__device is None or self.__acquisition_running is True:
            return False

        try:
            max_fps = self.__nodemap_remote_device.FindNode("AcquisitionFrameRate").Maximum()
            target_fps = min(max_fps, FPS_LIMIT)
            self.__nodemap_remote_device.FindNode("AcquisitionFrameRate").SetValue(target_fps)
        except ids_peak.Exception:
            pass

        self.__acquisition_timer.setInterval((1 / target_fps) * 1000)
        self.__acquisition_timer.setSingleShot(False)
        self.__acquisition_timer.timeout.connect(self.on_acquisition_timer)

        try:
            self.__nodemap_remote_device.FindNode("TLParamsLocked").SetValue(1)
            self.__datastream.StartAcquisition()
            self.__nodemap_remote_device.FindNode("AcquisitionStart").Execute()
            self.__nodemap_remote_device.FindNode("AcquisitionStart").WaitUntilDone()
        except Exception:
            return False

        self.__acquisition_timer.start()
        self.__acquisition_running = True
        return True

    def __stop_acquisition(self):
        if self.__device is None or self.__acquisition_running is False:
            return

        try:
            remote_nodemap = self.__device.RemoteDevice().NodeMaps()[0]
            remote_nodemap.FindNode("AcquisitionStop").Execute()

            self.__datastream.KillWait()
            self.__datastream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)
            self.__datastream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)
            self.__acquisition_running = False

            if self.__nodemap_remote_device is not None:
                try:
                    self.__nodemap_remote_device.FindNode("TLParamsLocked").SetValue(0)
                except Exception:
                    pass

        except Exception:
            pass

    @Slot()
    def on_acquisition_timer(self):
        try:
            buffer = self.__datastream.WaitForFinishedBuffer(5000)
            ipl_image = ids_peak_ipl_extension.BufferToImage(buffer)
            converted_ipl_image = self.__image_converter.Convert(ipl_image, TARGET_PIXEL_FORMAT)
            self.__datastream.QueueBuffer(buffer)
            image_np_array = converted_ipl_image.get_numpy_1D()
            image = QImage(image_np_array, converted_ipl_image.Width(), converted_ipl_image.Height(), QImage.Format_RGB32)
            image_cpy = image.copy()
            self.display.on_image_received(image_cpy)
            self.display.update()
        except ids_peak.Exception:
            pass