from PySide6.QtWidgets import QApplication

from pyside6helpers import css
from pyside6helpers import resources
from pyside6helpers.main_window import MainWindow

from ledboardtranslatoremulator.central_widget import CentralWidget


if __name__ == "__main__":
    """
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
    """
    import time

    import mido

    from ledboarddesktop.artnet.broadcaster import ArtnetBroadcaster

    broadcaster = ArtnetBroadcaster('127.0.0.1')
    broadcaster.add_universe(0)

    midi_in = mido.open_input('Frangitron virtual MIDI port', virtual=True)

    message_counter = 0
    message_counter_timestamp = time.time()

    previous_timestamp = time.time()
    message = None
    while True:
        try:
            message = midi_in.receive(block=False)
            if message is not None:
                message_counter += 1

                if message.type == 'control_change':
                    channel = (message.control - 1) + message.channel * 20
                    broadcaster.universes[0].buffer[channel] = message.value * 2

            now = time.time()
            if now - previous_timestamp >= (1.0 / 40.0):
                previous_timestamp = now
                broadcaster.send_data()

            if now - message_counter_timestamp >= 1.0:
                message_counter_timestamp = now
                print(f"Received {message_counter} MIDI messages in the last second")
                message_counter = 0

        except KeyboardInterrupt:
            break

    midi_in.close()
    print("Exiting")
