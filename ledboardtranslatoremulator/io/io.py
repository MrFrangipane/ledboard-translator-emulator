from  DMXEnttecPro import Controller as DMXEnttecPro

from PySide6.QtCore import QObject, QThread, Slot
from PySide6.QtWidgets import QApplication

from ledboardlib import InteropDataStore

from pyside6helpers import resources

from pythonartnet.broadcaster import ArtnetBroadcaster

from ledboardtranslatoremulator.midi.input_process import MidiInputProcess
from ledboardtranslatoremulator.translators.midi import MidiTranslator


class IO(QObject):

    _ENABLE_ENTTEC = False

    def __init__(self):
        super().__init__()

        self._midi_in = MidiInputProcess(midi_port_name='OSC Artnet')

        self.broadcaster = ArtnetBroadcaster(target_ip='127.0.0.1')
        self.broadcaster.add_universe(0)

        self._enttec: DMXEnttecPro | None = DMXEnttecPro("COM18") if self._ENABLE_ENTTEC else None

        interop_store = InteropDataStore(resources.find_from(__file__, "interop-data-melinerion.json"))
        self._translator = MidiTranslator(
            fixtures=interop_store.data.fixtures,
            midi_input_process=self._midi_in
        )

        self._alerts = self._translator.detect_conflicts()
        if self._alerts:
            print("!! Conflicts detected:")
            print("\n".join(self._alerts))

        self._is_running = False

    def start(self):
        print("Artnet thread started")

        self._is_running = True
        self._midi_in.start()

        while self._is_running:
            QThread.currentThread().msleep(int(1000 / 50))
            self.broadcaster.universes[0].buffer = bytearray(self._translator.make_universe())

            if self._ENABLE_ENTTEC:
                self._enttec.channels = bytearray(self.broadcaster.universes[0].buffer)
                self._enttec.submit()

            self.broadcaster.send_data_synced()

        self._midi_in.stop()

    @Slot()
    def stop(self):
        self._is_running = False


def create_io_thread() -> tuple[QThread, IO]:
    print("Creating Artnet thread")

    io = IO()
    thread = QThread()
    io.moveToThread(thread)

    def _stop():
        io.stop()
        thread.quit()
        thread.wait()

    QApplication.instance().aboutToQuit.connect(_stop)

    thread.started.connect(io.start)
    thread.finished.connect(thread.deleteLater)

    return thread, io
