import mido
from mido.ports import BaseInput
from PySide6.QtCore import QObject, Signal


class Midi(QObject):
    messageReceived = Signal(mido.Message)

    def __init__(self):
        super().__init__()
        self._midi_in: BaseInput = mido.open_input('Frangitron virtual MIDI port', virtual=True)
        self._midi_in.callback = lambda msg: self.messageReceived.emit(msg)
