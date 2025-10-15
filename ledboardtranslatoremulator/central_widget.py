import subprocess
import sys

from PySide6.QtCore import QThread
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QApplication

from mido import Message

from ledboardtranslatoremulator.dmx.dmx import create_dmx_thread, Dmx
from ledboardtranslatoremulator.midi.midi import create_midi_thread, Midi


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.dmx: Dmx | None = None
        self.dmx_thread: QThread | None = None

        self.midi: Midi | None = None
        self.midi_thread: QThread | None = None

        self.layout = QVBoxLayout(self)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.layout.addWidget(self.text)

        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update)
        self.layout.addWidget(self.update_button)

        self.midi_thread, self.midi = create_midi_thread()
        self.midi.messageReceived.connect(self.on_midi)

        self.dmx_thread, self.dmx = create_dmx_thread()
        self.dmx_thread.start()

        QApplication.instance().aboutToQuit.connect(self.midi.stop)

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
                self.dmx.updateRequested.emit(1, message.value * 2)
