from PySide6.QtCore import QObject, QThread, Slot
from PySide6.QtWidgets import QApplication

from ledboardlib.fixture import Fixture

from pythonartnet.broadcaster import ArtnetBroadcaster

from ledboardtranslatoremulator.midi.input_process import MidiInputProcess
from ledboardtranslatoremulator.translator.translator import Translator


class IO(QObject):

    def __init__(self):
        super().__init__()

        self._midi_in = MidiInputProcess(midi_port_name='OSC Artnet')

        self._broadcaster = ArtnetBroadcaster(target_ip='127.0.0.1')
        self._broadcaster.add_universe(0)


        self._translator = Translator(
            fixtures=[
                Fixture(name="NOON 1", midi_channel=1, dmx_address=1, dmx_channel_count=9),
                Fixture(name="NOON 2", midi_channel=2, dmx_address=10, dmx_channel_count=9),
                Fixture(name="NOON 3", midi_channel=3, dmx_address=19, dmx_channel_count=9),
                Fixture(name="NOON 4", midi_channel=4, dmx_address=28, dmx_channel_count=9),
                Fixture(name="NOON 5", midi_channel=5, dmx_address=37, dmx_channel_count=9),
                Fixture(name="NOON 6", midi_channel=6, dmx_address=46, dmx_channel_count=9),
                Fixture(name="NOON 7", midi_channel=7, dmx_address=55, dmx_channel_count=9),
                Fixture(name="NOON 8", midi_channel=8, dmx_address=64, dmx_channel_count=9),
                Fixture(name="Melinerion", midi_channel=9, dmx_address=73, dmx_channel_count=12),
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
