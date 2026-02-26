from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QLabel, QLineEdit, QPushButton

from ledboardtranslatoremulator.settings.settings import EmulatorSettings
from ledboardtranslatoremulator.settings import store as settings_store


class SettingsWidget(QWidget):
    changed = Signal(EmulatorSettings)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._suspend_signals = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Show Details
        self.show_details_checkbox = QCheckBox("Show details")
        self.show_details_checkbox.setChecked(True)
        self.show_details_checkbox.stateChanged.connect(self._changed)
        layout.addWidget(self.show_details_checkbox)

        # Always on top
        self.always_on_top_checkbox = QCheckBox("Always on top")
        self.always_on_top_checkbox.stateChanged.connect(self._changed)
        layout.addWidget(self.always_on_top_checkbox)

        # Target IP
        layout.addWidget(QLabel("Target IP"))
        self.target_ip = QLineEdit()
        self.target_ip.textChanged.connect(self._changed)
        layout.addWidget(self.target_ip)

        # Save
        self.button_save = QPushButton("Save")
        self.button_save.clicked.connect(self._save)
        layout.addWidget(self.button_save)

        layout.addStretch()

        # Message
        self.message_label = QLabel()
        layout.addWidget(self.message_label)

    def set_message(self, message: str):
        self.message_label.setText(message)

    def set_settings(self, settings: EmulatorSettings):
        self._suspend_signals = True

        self.always_on_top_checkbox.setChecked(settings.always_on_top)
        self.show_details_checkbox.setChecked(settings.show_details)
        self.target_ip.setText(settings.target_ip)

        self._suspend_signals = False

    def get_settings(self) -> EmulatorSettings:
        target_ip_text = self.target_ip.text().strip()
        return EmulatorSettings(
            always_on_top=self.always_on_top_checkbox.isChecked(),
            show_details=self.show_details_checkbox.isChecked(),
            target_ip=target_ip_text if target_ip_text else None
        )

    def load(self):
        self.set_settings(settings_store.load())

    def _changed(self):
        if self._suspend_signals:
            return

        self.changed.emit(self.get_settings())

    def _save(self):
        settings_store.save(self.get_settings())
