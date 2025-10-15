from PySide6.QtWidgets import QApplication, QLabel

from pyside6helpers import css
from pyside6helpers import resources
from pyside6helpers.main_window import MainWindow

import os
import sys

# Determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.join(sys._MEIPASS, 'ledboardtranslatoremulator')
else:
    application_path = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationName("LED Board Translator Emulator")
    app.setOrganizationName("Frangitron")
    css.load_onto(app)

    window = MainWindow(
        #logo_filepath=resources.find_from(application_path, "frangitron-logo.png"),
    )
    window.setCentralWidget(QLabel(__file__ + '\n' + __name__))
    window.show()

    app.exec()
