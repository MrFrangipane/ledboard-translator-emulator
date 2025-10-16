from PySide6.QtCore import QThread
from PySide6.QtWidgets import QWidget, QVBoxLayout

from ledboardtranslatoremulator.emulator.renderer_widget import LedRendererEmulatorWidget
from ledboardtranslatoremulator.io.io import IO, create_io_thread

from ledboardtranslatoremulator.updater.widget import UpdateWidget


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.io: IO | None = None
        self.io_thread: QThread | None = None
        self.io_thread, self.io = create_io_thread()

        layout = QVBoxLayout(self)

        # FIXME use components singleton
        self.led_renderer_emulator = LedRendererEmulatorWidget(broadcaster=self.io.broadcaster)
        layout.addWidget(self.led_renderer_emulator)

        layout.addWidget(UpdateWidget())

        layout.setStretch(0, 100)

        self.io_thread.start()
