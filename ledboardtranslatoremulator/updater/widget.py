from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

from ledboardtranslatoremulator.updater.updater import update_full, update_quick


class UpdateWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        button_update_quick = QPushButton("Quick update...")
        button_update_quick.clicked.connect(update_quick)
        layout.addWidget(button_update_quick)

        button_update_full = QPushButton("Full update...")
        button_update_full.clicked.connect(update_full)
        layout.addWidget(button_update_full)
