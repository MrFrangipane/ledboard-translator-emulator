import os

from ledboardlib import InteropDataStore
from ledboardtranslatoremulator.settings.settings import EmulatorSettings
from pyside6helpers import resources


def _make_settings_filepath() -> str:
    return os.path.expanduser("~/Frangitron/ledboard-translator-emulator-settings.json")


def save(settings: EmulatorSettings):
    filepath = _make_settings_filepath()
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    with open(filepath, "w") as file:
        file.write(settings.to_json(indent=2))


def load() -> EmulatorSettings:
    filepath = _make_settings_filepath()
    if not os.path.exists(filepath):
        print(f"No file found at {filepath}, using default settings.")
        return EmulatorSettings()

    with open(filepath, "r") as file:
        return EmulatorSettings.from_json(file.read())


def patch_from_interop():
    settings = load()

    interop_filepath = resources.find_from(__file__, "interop-data-melinerion.json")
    interop_data = InteropDataStore(interop_filepath).data

    if settings.target_ip is None:
        print(f"No target IP found in settings file, patching using interop : {interop_data.artnet_target_ip}")
        settings.target_ip = interop_data.artnet_target_ip

    save(settings)
