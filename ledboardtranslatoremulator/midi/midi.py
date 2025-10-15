import mido
from mido.ports import BaseInput
from PySide6.QtCore import QObject, Signal, QThread


class Midi(QObject):
    def __init__(self):
        super().__init__()
        self._midi_in: BaseInput | None = None
        self._is_running = False
        self.universe = bytearray(512)

    def start(self):
        print("MIDI thread started")
        self._is_running = True
        self._midi_in = mido.open_input('Frangitron virtual MIDI port', virtual=True)
        while self._is_running:
            message = self._midi_in.receive(block=False)
            if message is not None and message.type == 'control_change':
                print(message.channel)
                channel = (message.control - 1) + message.channel * 10
                self.universe[channel] = message.value * 2

        print("MIDI thread stopped")

    def stop(self):
        self._is_running = False
        self._midi_in.close()

def create_midi_thread() -> tuple[QThread, Midi]:
    print("Creating MIDI thread")
    thread = QThread()
    midi = Midi()
    midi.moveToThread(thread)
    thread.started.connect(midi.start)
    return thread, midi
