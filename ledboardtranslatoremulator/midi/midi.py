import mido
from mido.ports import BaseInput
from PySide6.QtCore import QObject, Signal, QThread


class Midi(QObject):
    messageReceived = Signal(mido.Message)
    stopRequested = Signal()

    def __init__(self):
        super().__init__()
        self._midi_in: BaseInput | None = None
        self._is_running = False
        self.stopRequested.connect(lambda: setattr(self, "_is_running", False))

    def start(self):
        self._is_running = True
        self._midi_in = mido.open_input('Frangitron virtual MIDI port', virtual=True)
        for message in self._midi_in:
            self.messageReceived.emit(message)
            if not self._is_running:
                break

        print("MIDI thread stopped")

def create_midi_thread() -> tuple[QThread, Midi]:
    thread = QThread()
    midi = Midi()
    midi.moveToThread(thread)
    thread.started.connect(midi.start)
    return thread, midi
