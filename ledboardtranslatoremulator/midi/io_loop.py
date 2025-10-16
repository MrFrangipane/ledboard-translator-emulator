from multiprocessing import Event
from multiprocessing.shared_memory import SharedMemory
import atexit
import signal
import sys
import time

import rtmidi


def _cleanup(shared_memory, midi_in):
    """Clean up resources properly"""
    if shared_memory is not None:
        shared_memory.close()
    if midi_in is not None:
        midi_in.close_port()
        del midi_in
    print("Resources cleaned up")


def _midi_callback(message, time_stamp, shared_memory):
    """Handle incoming MIDI messages"""
    if len(message) >= 3:
        status_byte, data_byte1, data_byte2 = message
        # Check if it's a control change message (0xB0-0xBF)
        if (status_byte & 0xF0) == 0xB0:
            channel = status_byte & 0x0F  # Extract MIDI channel (0-15)
            control = data_byte1 - 1  # Controller number (0-12-)
            value = data_byte2  # Controller value (0-126)

            channel_index = control + channel * 127
            shared_memory.buf[channel_index] = value


def _signal_handler(sig, frame):
    """
    Handle signals (e.g., SIGINT, SIGTERM) to exit gracefully.
    """
    print(f"\nReceived signal {sig}, exiting...")
    sys.exit(0)


def io_loop(port_name: str, shared_buffer_name: str, stop_event: Event):
    """Main I/O loop for MIDI input"""
    print("Starting MIDI input loop...")
    shared_memory = None
    midi_in = None

    try:
        shared_memory = SharedMemory(name=shared_buffer_name)

        midi_in = rtmidi.MidiIn()

        available_ports = midi_in.get_ports()
        port_index = None
        for i, name in enumerate(available_ports):
            if port_name in name:
                port_index = i
                break

        if port_index is not None:
            midi_in.open_port(port_index)
            print(f"Connected to existing MIDI port: {available_ports[port_index]}")
        else:
            midi_in.open_virtual_port(port_name)
            print(f"Created virtual MIDI input port: {port_name}")

        midi_in.set_callback(lambda data, _: _midi_callback(data[0], data[1], shared_memory))

        atexit.register(lambda: _cleanup(shared_memory, midi_in))

        signal.signal(signal.SIGINT, _signal_handler)  # Ctrl+C
        signal.signal(signal.SIGTERM, _signal_handler)  # Termination signal

        while not stop_event.is_set():
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        _cleanup(shared_memory, midi_in)
        print("Exiting")


if __name__ == "__main__":
    shared_memory = SharedMemory(create=True, size=2048)
    io_loop(sys.argv[1], shared_memory.name)

    print("MIDI input is active. Press Ctrl+C to exit.")

    shared_memory.close()
    shared_memory.unlink()
