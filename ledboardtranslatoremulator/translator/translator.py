from ledboardlib.fixture import Fixture

from ledboardtranslatoremulator.midi.input_process import MidiInputProcess



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
                address = fixture.dmx_address + dmx_channel
                value = self._midi.get_value(fixture.midi_channel, dmx_channel) * 2
                universe[address - 1] = value

        return universe
