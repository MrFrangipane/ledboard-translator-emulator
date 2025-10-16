from dataclasses import dataclass

from dataclasses_json import dataclass_json

from ledboardtranslatoremulator.midi.input_process import MidiInputProcess


@dataclass_json
@dataclass
class Fixture:
    name: str
    midi_channel: int
    dmx_address: int
    dmx_channel_count: int


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
        for fixture in self._fixtures:
            for dmx_channel in range(fixture.dmx_channel_count):
                universe[fixture.dmx_address + dmx_channel] = self._midi.get_value(fixture.midi_channel, dmx_channel) * 2

        return universe
