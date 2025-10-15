import subprocess
import sys
from DMXEnttecPro import Controller
from serial.tools.list_ports import comports

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QApplication
from mido import Message

from ledboardtranslatoremulator.midi.midi import Midi


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.layout.addWidget(self.text)

        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update)
        self.layout.addWidget(self.update_button)

        self.dmx: Controller | None = None
        ports = comports()
        enttec_found = False
        self.text.append(f"Found {len(ports)} COM ports")
        for port in ports:
            if "usbserial-EN" in port.device:
                self.text.append(f"Found enttec: {port}")
                self.dmx = Controller(port.device)
                enttec_found = True
                break

        if not enttec_found:
            self.text.append("No Enttec DMX found")

        self.midi = Midi()
        self.midi.messageReceived.connect(self.on_midi)

    def update(self):
        QApplication.instance().quit()
        QApplication.processEvents()
        subprocess.check_output([
            "pip", "install", "--force-reinstall",
            "git+https://github.com/MrFrangipane/ledboard-translator-emulator.git"
        ])
        subprocess.run([sys.executable] + sys.argv)
        sys.exit()

    def on_midi(self, message: Message):
        if message.type == 'control_change':
            if self.dmx is None:
                self.text.append(f"No DMX to forward MIDI message: {message}")
            else:
                self.dmx.set_channel(1, message.value * 2)
                self.dmx.submit()
