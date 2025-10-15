import time
from multiprocessing import shared_memory

import mido


def process_midi(shared_buffer_name):
    shm = shared_memory.SharedMemory(name=shared_buffer_name)
    midi_in = mido.open_input('Frangitron virtual MIDI port', virtual=True)

    message_counter = 0
    message_counter_timestamp = time.time()

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
