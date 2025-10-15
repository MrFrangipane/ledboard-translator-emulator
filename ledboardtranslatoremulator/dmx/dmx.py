from serial.tools.list_ports import comports
from mido.ports import BaseInput
from PySide6.QtCore import QObject, Signal, QThread
from DMXEnttecPro import Controller


class Dmx(QObject):

    def __init__(self):
        super().__init__()
        self._midi_in: BaseInput | None = None
        self._is_running = False
        self.midi = None
        self._should_restart = False
        self.dmx: Controller | None = None

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
        self._should_restart = False
        while self._is_running:
            QThread.currentThread().msleep(int(1000 / 40))
            self.dmx.channels = self.midi.universe
            try:
                self.dmx.submit()
            except IOError:
                self._should_restart = True
                break

        if self._should_restart:
            self.dmx.close()
            self.dmx = None
            self.start()


def create_dmx_thread() -> tuple[QThread, Dmx]:
    print("Creating DMX thread")
    thread = QThread()
    dmx = Dmx()
    dmx.moveToThread(thread)
    thread.started.connect(dmx.start)
    return thread, dmx
