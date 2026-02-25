from copy import copy
from dataclasses import fields
from importlib import resources

from ledboardlib import Fixture, ControlParameters, InteropDataStore, MappingMode, ColorMode
from ledboardlib.dmx_attribution.c_struct import DmxAttributionStruct


class ArtnetTranslator:
    def __init__(self, fixture: Fixture):
        self._fixture = fixture

        resource_path = str(resources.files('ledboardtranslatoremulator.resources') / 'interop-data-elephanz.json')
        interop_store = InteropDataStore(resource_path)
        self._default_parameters = interop_store.data.default_control_parameters

    def translate(self, universe: bytearray) -> ControlParameters:
        parameters = copy(self._default_parameters)

        # FIXME use introspection ? get it from board and put it in interop data
        for field in fields(DmxAttributionStruct):
            if field.default > 0:  # Using the condition from C++ code (dmxAttribution.X > 0)

                # Noise octaves (1-6)
                if field.name == "noise_octaves":
                    parameters.noise_octaves = 1 + universe[self._fixture.dmx_address - 2 + field.default] // 51

                # Noise global scale (1-16)
                elif field.name == "noise_scale":
                    parameters.noise_scale = 1 + universe[self._fixture.dmx_address - 2 + field.default] // 17

                # Noise axis scale (0-512)
                elif field.name in ["noise_scale_x", "noise_scale_y"]:
                    setattr(parameters, field.name, universe[self._fixture.dmx_address - 2 + field.default] * 2)

                # Noise speed (-255 to 255)
                elif field.name in ["noise_speed_x", "noise_speed_y", "noise_speed_z"]:
                    if universe[self._fixture.dmx_address - 2 + field.default] == 128:
                        setattr(parameters, field.name, 0)
                    else:
                        setattr(parameters, field.name, universe[self._fixture.dmx_address - 2 + field.default] * 2 - 255)

                # Noise min max (0-1024)
                elif field.name in ["noise_min", "noise_max"]:
                    setattr(parameters, field.name, universe[self._fixture.dmx_address - 2 + field.default] * 4)

                # Mapping mode
                elif field.name == "mapping_mode":
                    parameters.mapping_mode = MappingMode(universe[self._fixture.dmx_address - 2 + field.default] // 128)

                # Color mode
                elif field.name == "color_mode":
                    parameters.color_mode = ColorMode(universe[self._fixture.dmx_address - 2 + field.default] // 128)

                # Direct value assignments (0-255)
                elif field.name in ["noise_h", "noise_s", "noise_l", "noise_r", "noise_g", "noise_b",
                                    "runner_h", "runner_s", "runner_l", "runner_r", "runner_g", "runner_b", "shutter"]:
                    setattr(parameters, field.name, universe[self._fixture.dmx_address - 2 + field.default])

                # Runner trigger
                elif field.name in ["runner_trigger", "are_colors_inverted", "is_noise_on"]:
                    parameters.runner_trigger = bool(universe[self._fixture.dmx_address - 2 + field.default] // 128)

                # Mask positions (-255 to 255)
                elif field.name in ["mask_x1", "mask_x2", "mask_y1", "mask_y2"]:
                    setattr(parameters, field.name, universe[self._fixture.dmx_address - 2 + field.default] * 2 - 255)

        return parameters
