from ledboardlib.fixture import Fixture

from ledboardtranslatoremulator.midi.input_process import MidiInputProcess



class MidiTranslator:
    """
    Translates MIDI CC values to DMX values, according to configured Fixtures
    """
    # FIXME make indirection for MidiInputProcess ?
    def __init__(self, fixtures: list[Fixture], midi_input_process: MidiInputProcess):
        self._fixtures = fixtures
        self._midi = midi_input_process

    def detect_conflicts(self) -> list[str]:
        used_channels = [""] * 512
        alert_messages = list()
        for fixture in self._fixtures:
            for dmx_channel in range(fixture.dmx_channel_count):
                address = fixture.dmx_address + dmx_channel
                if used_channels[address] != "":
                    alert_messages.append(f"Fixture {fixture.name} DMX channel {dmx_channel + 1} is already used by {used_channels[address]}")
                else:
                    used_channels[address - 1] = f"{fixture.name} channel {dmx_channel + 1}"

        return alert_messages

    def make_universe(self) -> list[int]:
        universe = [0] * 512
        for fixture in self._fixtures:
            for dmx_channel in range(fixture.dmx_channel_count):
                address = fixture.dmx_address + dmx_channel
                value = self._midi.get_value(fixture.midi_channel - 1, dmx_channel) * 2
                universe[address - 1] = value

        return universe
