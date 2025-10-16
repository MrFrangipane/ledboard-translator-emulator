from copy import copy
from dataclasses import fields

from ledboardlib import Fixture, ControlParameters, InteropDataStore
from ledboardlib.dmx_attribution.c_struct import DmxAttributionStruct
from pyside6helpers import resources


class ArtnetTranslator:
    def __init__(self, fixture: Fixture):
        self._fixture = fixture

        interop_store = InteropDataStore(resources.find_from(__file__, "interop-data-melinerion.json"))
        self._default_parameters = interop_store.data.default_control_parameters

    def translate(self, universe: list[int]) -> ControlParameters:
        parameters = copy(self._default_parameters)

        start = self._fixture.dmx_address - 1
        end = self._fixture.dmx_address + self._fixture.dmx_channel_count - 1
        values = universe[start:end]

        attribution = DmxAttributionStruct()  # FIXME: get it from board and put it in interop data
        for field in fields(attribution):
            if field.default != 0:
                parameters.__setattr__(field.name, values[field.default - 1])

        return parameters
