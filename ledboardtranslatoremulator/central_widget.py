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

        ports = comports()
        self.text.append(f"Found {len(ports)} ports")
        for port in ports:
            self.text.append(f"{port.device}")

        self.dmx = Controller(ports[0].device)

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
            self.dmx.set_channel(1, message.value * 2)
