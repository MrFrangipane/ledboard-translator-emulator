import subprocess
import sys

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QApplication

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

        self.midi = Midi()
        self.midi.messageReceived.connect(lambda message: self.text.append(f"{message}\n"))

    def update(self):
        QApplication.instance().quit()
        QApplication.processEvents()
        subprocess.check_output([
            "pip", "install", "--force-reinstall",
            "git+https://github.com/MrFrangipane/ledboard-translator-emulator.git"
        ])
        subprocess.run([sys.executable] + sys.argv)
        sys.exit()
