from PySide6.QtWidgets import QApplication, QLabel

from pyside6helpers import css
from pyside6helpers import resources
from pyside6helpers.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationName("LED Board Translator Emulator")
    app.setOrganizationName("Frangitron")
    css.load_onto(app)

    window = MainWindow(
        logo_filepath=resources.find_from(__file__, "frangitron-logo.png"),
    )
    window.setCentralWidget(QLabel(__file__ + '\n' + __name__))
    window.show()

    app.exec()
