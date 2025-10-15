import subprocess
import sys

from PySide6.QtWidgets import QApplication, QPushButton

from pyside6helpers import css
from pyside6helpers import resources
from pyside6helpers.main_window import MainWindow


def update():
    subprocess.check_output(["pip", "install", "--force-reinstall", "git+https://github.com/MrFrangipane/ledboard-translator-emulator.git"])
    subprocess.run(sys.argv)
    sys.exit()


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationName("LED Board Translator Emulator")
    app.setOrganizationName("Frangitron")
    css.load_onto(app)

    window = MainWindow(
        logo_filepath=resources.find_from(__file__, "frangitron-logo.png"),
    )

    button = QPushButton("Update")
    button.clicked.connect(update)

    window.setCentralWidget(button)
    window.show()

    app.exec()
