from dataclasses import dataclass

from dataclasses_json import dataclass_json

from ledboardtranslatoremulator.midi.input_process import MidiInputProcess


@dataclass_json
@dataclass
class Fixture:
    pass


class Translator:
    """
    Translates MIDI CC values to DMX values, according to configured Fixtures
    """
    # FIXME make indirection for MidiInputProcess ?
    def __init__(self, fixtures: list[Fixture], midi_input_process: MidiInputProcess):
        self._fixtures = fixtures
        self._midi = midi_input_process

    def make_universe(self) -> list[int]:
        universe = [0] * 512
        return universe
