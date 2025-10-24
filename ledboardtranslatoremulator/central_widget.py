from PySide6.QtCore import QThread
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel

from ledboardtranslatoremulator.emulator.renderer_widget import LedRendererEmulatorWidget
from ledboardtranslatoremulator.io.io import IO, create_io_thread
from ledboardtranslatoremulator.settings.settings import EmulatorSettings
from ledboardtranslatoremulator.settings.widget import SettingsWidget
from ledboardtranslatoremulator.updater.widget import UpdateWidget


class CentralWidget(QWidget):
    def __init__(self, set_always_on_top, parent=None):
        super().__init__(parent)

        self._set_always_on_top_callback = set_always_on_top

        # IO
        self.io: IO | None = None
        self.io_thread: QThread | None = None
        self.io_thread, self.io = create_io_thread()
        self.io.errorOccurred.connect(lambda msg: self.settings_wdiget.set_message(msg))
        self.io.started.connect(lambda: self.settings_wdiget.set_message("IO started"))

        layout = QGridLayout(self)

        # Settings
        self.settings_wdiget = SettingsWidget()
        self.settings_wdiget.set_message("Waiting for IO to start")
        self.settings_wdiget.changed.connect(self._settings_changed)
        layout.addWidget(self.settings_wdiget, 0, 0, 1, 2)

        # Renderer emulator
        # FIXME use components singleton
        self.led_renderer_emulator = LedRendererEmulatorWidget(broadcaster=self.io.broadcaster)
        layout.addWidget(self.led_renderer_emulator, 1, 0)
        layout.setColumnStretch(0, 100)
        layout.setRowStretch(1, 100)

        # Details
        self.details_label = QLabel()
        self.led_renderer_emulator.detailsUpdated.connect(self.details_label.setText)
        layout.addWidget(self.details_label, 1, 1)

        # Update
        layout.addWidget(UpdateWidget(), 2, 0, 1, 2)

        self.settings_wdiget.load()
        self.io_thread.start()

    def _settings_changed(self, settings: EmulatorSettings):
        self._set_always_on_top_callback(settings.always_on_top)
        self.details_label.setVisible(settings.show_details)
