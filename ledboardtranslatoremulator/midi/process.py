from multiprocessing import shared_memory

import mido


def process_midi(shared_buffer_name):
    shared_memory_buffer = shared_memory.SharedMemory(name=shared_buffer_name)

    midi_in = mido.open_input('Frangitron virtual MIDI port', virtual=True)

    while True:
        try:
            message = midi_in.receive(block=False)
            if message is not None:

                if message.type == 'control_change':
                    channel = (message.control - 1) + message.channel * 127
                    shared_memory_buffer.buf[channel] = message.value * 2

        except KeyboardInterrupt:
            break

    midi_in.close()
    print("Exiting")
