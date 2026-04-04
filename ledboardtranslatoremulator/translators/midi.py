from importlib import resources

from ledboardlib import InteropDataStore
from ledboardlib.fixture import Fixture

from ledboardtranslatoremulator.midi.input_process import MidiInputProcess



class MidiTranslator:
    """
    Translates MIDI CC values to DMX values, according to configured Fixtures
    """
    # FIXME make indirection for MidiInputProcess ?
    def __init__(self, fixtures: list[Fixture], midi_input_process: MidiInputProcess, blackout_on_stop: bool):
        self._fixtures = fixtures
        self._midi = midi_input_process
        self._blackout_on_stop = blackout_on_stop

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

        if self._midi.is_playing() or not self._blackout_on_stop:
            for fixture in self._fixtures:
                for dmx_channel in range(fixture.dmx_channel_count):
                    address = fixture.dmx_address + dmx_channel
                    value = self._midi.get_value(fixture.midi_channel - 1, dmx_channel) * 2
                    universe[address - 1] = value

        return universe
