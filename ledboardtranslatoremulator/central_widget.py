from PySide6.QtCore import QThread
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox

from ledboardtranslatoremulator.emulator.renderer_widget import LedRendererEmulatorWidget
from ledboardtranslatoremulator.io.io import IO, create_io_thread

from ledboardtranslatoremulator.updater.widget import UpdateWidget


class CentralWidget(QWidget):
    def __init__(self, set_always_on_top, parent=None):
        super().__init__(parent)

        # IO
        self.io: IO | None = None
        self.io_thread: QThread | None = None
        self.io_thread, self.io = create_io_thread()
        self.io.errorOccurred.connect(lambda msg: self.message_label.setText(msg))
        self.io.started.connect(lambda: self.message_label.setText("IO started"))

        layout = QGridLayout(self)

        # Renderer emulator
        # FIXME use components singleton
        self.led_renderer_emulator = LedRendererEmulatorWidget(broadcaster=self.io.broadcaster)
        layout.addWidget(self.led_renderer_emulator, 3, 0)
        layout.setColumnStretch(0, 100)
        layout.setRowStretch(3, 100)

        # Details
        details_label = QLabel()
        self.led_renderer_emulator.detailsUpdated.connect(details_label.setText)
        layout.addWidget(details_label, 3, 1)

        show_details_checkbox = QCheckBox("Show details")
        show_details_checkbox.setChecked(True)
        show_details_checkbox.stateChanged.connect(lambda state: details_label.setVisible(state == 2))
        layout.addWidget(show_details_checkbox, 0, 0, 1, 2)

        # Always on top
        always_on_top_checkbox = QCheckBox("Always on top")
        always_on_top_checkbox.stateChanged.connect(lambda state: set_always_on_top(state == 2))
        layout.addWidget(always_on_top_checkbox, 1, 0, 1, 2)

        # Message
        self.message_label = QLabel("Waiting for IO to start")
        layout.addWidget(self.message_label, 2, 0, 1, 2)

        # Update
        layout.addWidget(UpdateWidget(), 4, 0, 1, 2)

        self.io_thread.start()
