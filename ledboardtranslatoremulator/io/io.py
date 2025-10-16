from PySide6.QtCore import QObject, QThread, Slot
from PySide6.QtWidgets import QApplication

from pythonartnet.broadcaster import ArtnetBroadcaster

from ledboardtranslatoremulator.midi.input_process import MidiInputProcess
from ledboardtranslatoremulator.translator.translator import Translator, Fixture


class IO(QObject):

    def __init__(self):
        super().__init__()

        self._midi_in = MidiInputProcess(midi_port_name='OSC Artnet')

        self._broadcaster = ArtnetBroadcaster(target_ip='127.0.0.1')
        self._broadcaster.add_universe(0)

        self._translator = Translator(
            fixtures=[
                Fixture(name="Melinerion", midi_channel=1, dmx_address=0, dmx_channel_count=12),
            ],
            midi_input_process=self._midi_in,
        )

        self._is_running = False

    def start(self):
        print("Artnet thread started")

        self._is_running = True
        self._midi_in.start()

        while self._is_running:
            QThread.currentThread().msleep(int(1000 / 40))
            self._broadcaster.universes[0].buffer = bytearray(self._translator.make_universe())
            self._broadcaster.send_data_synced()

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
