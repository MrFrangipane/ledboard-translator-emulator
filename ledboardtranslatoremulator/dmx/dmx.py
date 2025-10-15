import time

from serial.tools.list_ports import comports
from mido.ports import BaseInput
from PySide6.QtCore import QObject, Signal, QThread
from DMXEnttecPro import Controller


class Dmx(QObject):

    def __init__(self):
        super().__init__()
        self._midi_in: BaseInput | None = None
        self._is_running = False
        self._latest_submit_timestamp = time.time()
        self.midi = None

    def start(self):
        print("DMX thread started")
        ports = comports()
        for port in ports:
            if "usbserial-EN" in port.device:
                self.dmx = Controller(port.device)
                print(f"DMX connected on {port.device}")
                break

        if self.dmx is None:
            print("DMX not connected")
            return

        self._is_running = True
        while self._is_running:

            elapsed = time.time() - self._latest_submit_timestamp
            if elapsed >= 1.0 / 40.0:
                self.dmx.channels = self.midi.universe
                self.dmx.submit()


def create_dmx_thread() -> tuple[QThread, Dmx]:
    print("Creating DMX thread")
    thread = QThread()
    dmx = Dmx()
    dmx.moveToThread(thread)
    thread.started.connect(dmx.start)
    return thread, dmx
