from PySide6.QtCore import QThread
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QApplication

from ledboardtranslatoremulator.io.io import IO, create_io_thread

from ledboardtranslatoremulator.updater.widget import UpdateWidget


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.io: IO | None = None
        self.io_thread: QThread | None = None

        self.layout = QVBoxLayout(self)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.layout.addWidget(self.text)

        self.layout.addWidget(UpdateWidget())

        self.io_thread, self.io = create_io_thread()
        self.io_thread.start()
