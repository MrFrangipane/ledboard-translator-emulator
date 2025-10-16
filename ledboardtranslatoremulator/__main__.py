from PySide6.QtWidgets import QApplication

from pyside6helpers import css
from pyside6helpers import resources
from pyside6helpers.main_window import MainWindow

from ledboardtranslatoremulator.central_widget import CentralWidget


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationName("LED Board Translator Emulator")
    app.setOrganizationName("Frangitron")
    css.load_onto(app)

    window = MainWindow(
        logo_filepath=resources.find_from(__file__, "frangitron-logo.png"),
    )
    window.setWindowTitle("LED Board Translator Emulator")
    window.setCentralWidget(CentralWidget())
    window.show()

    app.exec()
