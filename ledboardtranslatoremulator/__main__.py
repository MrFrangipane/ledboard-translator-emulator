import multiprocessing

import time
from multiprocessing import shared_memory

from ledboardtranslatoremulator.midi.process import process_midi
from ledboarddesktop.artnet.broadcaster import ArtnetBroadcaster


if __name__ == "__main__":
    broadcaster = ArtnetBroadcaster('127.0.0.1')
    broadcaster.add_universe(0)

    shm = shared_memory.SharedMemory(create=True, size=2048)
    print(
        f"Created shared memory with name {shm.name} and size {shm.size}"
    )
    midi_process = multiprocessing.Process(
        target=process_midi,
        args=(shm.name,)
    )
    midi_process.start()
    print("started midi process")

    while True:
        try:
            time.sleep(1.0 / 40.0)
            for i in range(512):
                broadcaster.universes[0].buffer[i] = shm.buf[i]
            broadcaster.send_data()
            print(shm.buf[:20])

        except KeyboardInterrupt:
            break

    shm.close()
    shm.unlink()
