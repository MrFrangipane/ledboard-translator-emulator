import multiprocessing

import time
from multiprocessing import shared_memory

from ledboardtranslatoremulator.midi.process import process_midi

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

    from ledboarddesktop.artnet.broadcaster import ArtnetBroadcaster

    broadcaster = ArtnetBroadcaster('127.0.0.1')
    broadcaster.add_universe(0)

    shm = shared_memory.SharedMemory(create=True, size=512)
    midi_process = multiprocessing.Process(
        target=process_midi,
        args=shm.name
    )
    midi_process.start()

    while True:
        try:
            time.sleep(1.0 / 40.0)
            broadcaster.universes[0].buffer = bytearray(shm.buf)
            broadcaster.send_data()

        except KeyboardInterrupt:
            break

    shm.close()
    shm.unlink()
