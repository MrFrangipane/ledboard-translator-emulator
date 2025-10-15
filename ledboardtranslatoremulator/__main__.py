import multiprocessing

import time
from multiprocessing import shared_memory

import mido


def process_midi(shared_buffer_name):
    shm = shared_memory.SharedMemory(name=shared_buffer_name)
    midi_in = mido.open_input('Frangitron virtual MIDI port', virtual=True)

    message_counter = 0
    message_counter_timestamp = time.time()

    previous_timestamp = time.time()
    while True:
        try:
            message = midi_in.receive(block=False)
            if message is not None:
                message_counter += 1

                if message.type == 'control_change':
                    channel = (message.control - 1) + message.channel * 20
                    shm.buf[channel] = message.value * 2

            now = time.time()
            if now - message_counter_timestamp >= 1.0:
                message_counter_timestamp = now
                print(f"Received {message_counter} MIDI messages in the last second")
                message_counter = 0

        except KeyboardInterrupt:
            break

    midi_in.close()
    print("Exiting")



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
    shm.unlink()  #
