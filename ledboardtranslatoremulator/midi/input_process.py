import sys
import time
from multiprocessing import Process, Event
from multiprocessing.shared_memory import SharedMemory

from ledboardtranslatoremulator.midi.io_loop import io_loop


class MidiInputProcess:
    """
    Provides fast MIDI input processing through shared memory

    This class is designed to handle MIDI input asynchronously by using a child
    process and shared memory. It facilitates real-time MIDI CC message processing,
    allowing retrieval of control parameter values efficiently. The class ensures
    proper cleanup of resources, including shared memory and the child process.
    """
    def __init__(self, midi_port_name: str):
        self._stop_event = Event()
        self._midi_port_name: str = midi_port_name
        self._process_io: Process | None = None
        self._shared_memory = SharedMemory(create=True, size=2048)

    def start(self):
        """
        Starts the I/O process for handling MIDI communication and shared memory synchronization.
        If an existing I/O process is running, it will stop it before starting a new one.

        Raises:
            Any existing errors related to process handling can be thrown during the execution
            of starting or stopping the I/O process.
        """
        if self._process_io is not None:
            self.stop()

        self._stop_event.clear()
        self._process_io = Process(
            target=io_loop,
            args=(self._midi_port_name, self._shared_memory.name, self._stop_event)
        )
        self._process_io.start()

    def stop(self):
        """
        Stops the MIDI input process and cleans up resources.

        This method terminates the background MIDI input process, ensures that
        all system resources used by the process are released properly, and
        removes shared memory associated with the process.

        Raises:
            Any exceptions that may occur when terminating the process, joining
            the process thread, or accessing shared memory resources.
        """
        print("Stopping MIDI input process...")
        self._stop_event.set()
        self._process_io.join()
        self._process_io = None
        self._shared_memory.close()
        self._shared_memory.unlink()

    def get_value(self, channel: int, control: int) -> int:
        """
        Reads the value of a given channel and control from the shared memory buffer.

        Parameters:
            channel (int): The MIDI channel (0-15)
            control (int): The control number (0-126)

        Returns:
            int: The value read from the shared memory buffer
        """
        channel_index = control + channel * 127
        return self._shared_memory.buf[channel_index]


if __name__ == "__main__":
    midi_input_process = MidiInputProcess(sys.argv[1])
    midi_input_process.start()

    while True:
        try:
            print(midi_input_process.get_value(
                channel=1,
                control=0
            ))
            time.sleep(1.0 / 10.0)
        except KeyboardInterrupt:
            break

    midi_input_process.stop()
