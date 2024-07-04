from ids_peak import ids_peak, ids_peak_ipl_extension
from ids_peak_ipl import ids_peak_ipl
from ids_peak_afl import ids_peak_afl
from PIL import Image, ImageEnhance
import numpy as np
import sys

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
    # Gamma-Korrektur anwenden
    inv_gamma = 1.0 / gamma
    table = [((i / 255.0) ** inv_gamma) * 255 for i in range(256)]
    table = np.array(table).astype("uint8")
    return image.point(table)

def increase_brightness(image, factor=2.0):
    # Helligkeit erhöhen
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

def main():
    try:
        # Initialisierung der Bibliotheken
        ids_peak.Library.Initialize()
        ids_peak_afl.Library.Init()

        # Geräteverwaltung
        device_manager = ids_peak.DeviceManager.Instance()

        # Geräte aktualisieren
        device_manager.Update()

        # Kein Gerät gefunden
        if device_manager.Devices().empty():
            print("Kein Gerät gefunden. Beende das Programm.")
            return -1

        # Erstes Gerät öffnen
        device = device_manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Control)
        print(f"Gerät geöffnet: {device.SerialNumber()} -> {device.DisplayName()}")

        # Nodemap für GenICam-Zugriff
        remote_nodemap = device.RemoteDevice().NodeMaps()[0]

        # Autofeature-Manager und Controller erstellen
        manager = ids_peak_afl.Manager(remote_nodemap)
        controller = manager.CreateController(ids_peak_afl.PEAK_AFL_CONTROLLER_TYPE_BRIGHTNESS)

        print(f"Controller Status: {controller.Status()}")
        print(f"Controller Typ: {controller.Type()}")

        # Automatische Belichtung und Gain einstellen
        remote_nodemap.FindNode("ExposureAuto").SetCurrentEntry("Continuous")
        remote_nodemap.FindNode("GainAuto").SetCurrentEntry("Continuous")

        # Standardkameraeinstellungen laden
        remote_nodemap.FindNode("UserSetSelector").SetCurrentEntry("Default")
        remote_nodemap.FindNode("UserSetLoad").Execute()
        remote_nodemap.FindNode("UserSetLoad").WaitUntilDone()

        # Callbacks registrieren
        finished = FinishedCallback(controller)
        exposureFinished = ComponentExposureFinishedCallback(controller)
        gainFinished = ComponentGainFinishedCallback(controller)

        # Datenstrom öffnen und Buffer zuweisen
        data_stream = device.DataStreams()[0].OpenDataStream()
        payload_size = remote_nodemap.FindNode("PayloadSize").Value()
        buffer_count_max = data_stream.NumBuffersAnnouncedMinRequired()

        for _ in range(buffer_count_max):
            buffer = data_stream.AllocAndAnnounceBuffer(payload_size)
            data_stream.QueueBuffer(buffer)

        # Sperrung schreibbarer Knoten während der Erfassung
        remote_nodemap.FindNode("TLParamsLocked").SetValue(1)

        print("Starte Erfassung...")
        data_stream.StartAcquisition()
        remote_nodemap.FindNode("AcquisitionStart").Execute()
        remote_nodemap.FindNode("AcquisitionStart").WaitUntilDone()

        print("Erhalte 1 Bild...")
        for _ in range(1):
            try:
                buffer = data_stream.WaitForFinishedBuffer(5000)

                # Bild aus dem Buffer erstellen
                image = ids_peak_ipl.Image.CreateFromSizeAndBuffer(
                    buffer.PixelFormat(),
                    buffer.BasePtr(),
                    buffer.Size(),
                    buffer.Width(),
                    buffer.Height()
                )
                rgb_img = image.ConvertTo(ids_peak_ipl.PixelFormatName_BGRa8, ids_peak_ipl.ConversionMode_Fast)
                
                # Temporärer Speicherort für das Bild
                temp_image_path = "C:\\Users\\Administrator\\Desktop\\KAT\\Output\\temp.png"
                ids_peak_ipl.ImageWriter.Write(temp_image_path, rgb_img)
                
                # Bild mit PIL öffnen
                img = Image.open(temp_image_path)
                
                # Gamma-Korrektur anwenden
                img = apply_gamma_correction(img)
                
                # Helligkeit erhöhen
                img = increase_brightness(img)
                
                # Speichern des bearbeiteten Bildes
                final_image_path = "C:\\Users\\Administrator\\Desktop\\KAT\\Output\\clean_image.png"
                img.save(final_image_path)
                
                # Buffer zurück in die Warteschlange
                data_stream.QueueBuffer(buffer)
            except Exception as e:
                print(f"Ausnahme: {e}")

        print("Beende Erfassung...")
        remote_nodemap.FindNode("AcquisitionStop").Execute()
        remote_nodemap.FindNode("AcquisitionStop").WaitUntilDone()

        data_stream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)

        # Buffer entfernen
        data_stream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)

        for buffer in data_stream.AnnouncedBuffers():
            data_stream.RevokeBuffer(buffer)

        # Schreibbare Knoten entsperren
        remote_nodemap.FindNode("TLParamsLocked").SetValue(0)

        print(f"Letzter automatischer Durchschnitt: {controller.GetLastAutoAverage()}")

    except Exception as e:
        print(f"AUSNAHME: {e}")
        return -2

    finally:
        ids_peak_afl.Library.Exit()
        ids_peak.Library.Close()

if __name__ == '__main__':
    main()