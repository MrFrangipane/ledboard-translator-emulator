from  DMXEnttecPro import Controller as DMXEnttecPro

from PySide6.QtCore import QObject, QThread, Slot, Signal
from PySide6.QtWidgets import QApplication

from ledboardlib import InteropDataStore

from pyside6helpers import resources

from pythonartnet.broadcaster import ArtnetBroadcaster, ArtnetBroadcastError

from ledboardtranslatoremulator.midi.input_process import MidiInputProcess
from ledboardtranslatoremulator.settings import store as settings_store
from ledboardtranslatoremulator.translators.midi import MidiTranslator


class IO(QObject):
    started = Signal()
    errorOccurred = Signal(str)

    def __init__(self):
        super().__init__()

        self._artnet_enabled = True

        settings = settings_store.load()

        interop_filepath = resources.find_from(__file__, "interop-data-melinerion.json")
        interop_data = InteropDataStore(interop_filepath).data

        if settings.target_ip is None:
            print(f"No target IP found in settings file, using interop : {interop_data.artnet_target_ip}")
            settings.target_ip = interop_data.artnet_target_ip

        self._midi_in = MidiInputProcess(midi_port_name=interop_data.midi_port_name)

        self.broadcaster = ArtnetBroadcaster(target_ip=settings.target_ip)
        self.broadcaster.add_universe(0)

        self._enttec: DMXEnttecPro | None = None
        if interop_data.enttec_output_enabled:
            try:
                self._enttec = DMXEnttecPro(interop_data.enttec_port_name)
            except Exception as e:
                print(f"Failed to initialize Enttec Pro: {e}")

        self._translator = MidiTranslator(
            fixtures=interop_data.fixtures,
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

        self.started.emit()

        while self._is_running:
            QThread.currentThread().msleep(int(1000 / 50))
            self.broadcaster.universes[0].buffer = bytearray(self._translator.make_universe())

            if self._enttec is not None:
                self._enttec.channels = bytearray(self.broadcaster.universes[0].buffer)
                self._enttec.submit()

            if not self._artnet_enabled:
                continue

            try:
                self.broadcaster.send_data_synced()
            except ArtnetBroadcastError as e:
                self.errorOccurred.emit(f"Artnet disabled: {e}")
                self._artnet_enabled = False

        self._midi_in.stop()

        if self._enttec is not None:
            self._enttec.close()

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
