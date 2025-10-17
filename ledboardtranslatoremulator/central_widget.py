from PySide6.QtCore import QThread
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel

from ledboardtranslatoremulator.emulator.renderer_widget import LedRendererEmulatorWidget
from ledboardtranslatoremulator.io.io import IO, create_io_thread

from ledboardtranslatoremulator.updater.widget import UpdateWidget


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.io: IO | None = None
        self.io_thread: QThread | None = None
        self.io_thread, self.io = create_io_thread()

        layout = QGridLayout(self)

        # FIXME use components singleton
        self.led_renderer_emulator = LedRendererEmulatorWidget(broadcaster=self.io.broadcaster)
        layout.addWidget(self.led_renderer_emulator, 0, 0)
        layout.setColumnStretch(0, 100)
        layout.setRowStretch(0, 100)

        self.details_label = QLabel()
        self.led_renderer_emulator.detailsUpdated.connect(self.details_label.setText)
        layout.addWidget(self.details_label, 0, 1)

        layout.addWidget(UpdateWidget(), 1, 0, 1, 2)

        self.io_thread.start()
