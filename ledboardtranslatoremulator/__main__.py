import logging
logging.basicConfig(level=logging.INFO)

from importlib import resources as _resources

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ledboardtranslatoremulator.settings import store as settings_store
from pyside6helpers import css
from pyside6helpers.main_window import MainWindow

from ledboardtranslatoremulator.central_widget import CentralWidget


if __name__ == "__main__":
    settings_store.patch_from_interop()
    settings = settings_store.load()

    app = QApplication([])
    app.setApplicationName("LED Board Translator Emulator")
    app.setOrganizationName("Frangitron")
    css.load_onto(app)

    resource_path = _resources.files("ledboardtranslatoremulator.resources").joinpath('frangitron-logo.png')
    window = MainWindow(
        logo_filepath=str(resource_path),
    )
    window.setWindowTitle("LED Board Translator Emulator")

    def set_always_on_top(is_true):
        window.setWindowFlag(Qt.WindowStaysOnTopHint, is_true)
        window.show()

    window.setCentralWidget(CentralWidget(set_always_on_top))
    set_always_on_top(settings.always_on_top)

    app.exec()
