import subprocess
import sys

from PySide6.QtWidgets import QApplication


def update_quick():
    _update(extra_args=['--no-deps'])

def update_full():
    _update()


def _update(extra_args=None):
    if extra_args is None:
        extra_args = []

    QApplication.instance().quit()
    QApplication.processEvents()
    subprocess.check_output([
        "pip", "install", "--force-reinstall",
        "git+https://github.com/MrFrangipane/ledboard-translator-emulator.git"
    ] + extra_args)
    subprocess.run([sys.executable] + sys.argv)
    sys.exit()
