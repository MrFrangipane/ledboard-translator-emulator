from copy import copy

from PySide6.QtCore import QObject, QThread

from ledboarddesktop.artnet.broadcaster import ArtnetBroadcaster


class Artnet(QObject):

    def __init__(self):
        super().__init__()
        self._broadcaster = ArtnetBroadcaster('127.0.0.1')
        self._broadcaster.add_universe(0)
        self.midi = None
        self._is_running = False

    def start(self):
        print("Artnet thread started")

        self._is_running = True
        while self._is_running:
            QThread.currentThread().msleep(int(1000 / 40))
            self._broadcaster.universes[0].buffer = copy(self.midi.universe)
            self._broadcaster.send_data_synced()


def create_artnet_thread() -> tuple[QThread, Artnet]:
    print("Creating Artnet thread")
    thread = QThread()
    artnet = Artnet()
    artnet.moveToThread(thread)
    thread.started.connect(artnet.start)
    return thread, artnet
