from multiprocessing.shared_memory import SharedMemory

import mido


def process_midi(shared_buffer_name):
    shared_memory = SharedMemory(name=shared_buffer_name)

    midi_in = mido.open_input('Frangitron virtual MIDI port', virtual=True)

    while True:
        try:
            message = midi_in.receive()
            if message is not None:
                if message.type == 'control_change':
                    channel = (message.control - 1) + message.channel * 127
                    shared_memory.buf[channel] = message.value * 2
                    print(list(shared_memory.buf[:20]))

        except KeyboardInterrupt:
            break

    shared_memory.close()
    midi_in.close()
    print("Exiting")
