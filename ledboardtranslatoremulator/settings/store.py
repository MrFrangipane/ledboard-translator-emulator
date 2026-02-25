import os
import sys

from ledboardlib import InteropDataStore
from ledboardtranslatoremulator.settings.settings import EmulatorSettings


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

    interop_filepath = _find("interop-data-elephanz.json", __file__ )
    interop_data = InteropDataStore(interop_filepath).data

    if settings.target_ip is None:
        print(f"No target IP found in settings file, patching using interop : {interop_data.artnet_target_ip}")
        settings.target_ip = interop_data.artnet_target_ip

    save(settings)


def _find(resource_name: str, current_file: str | None = None) -> str:
    if current_file is None:
        current_file = sys.argv[0]

    current_dir = os.path.abspath(os.path.dirname(current_file))
    resources_dir = "resources"

    while current_dir:
        potential_resources_path = os.path.join(current_dir, resources_dir)
        if os.path.isdir(potential_resources_path):
            path = os.path.join(potential_resources_path, resource_name)
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Could not find {resource_name} in {potential_resources_path}")
            return path

        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break

        current_dir = parent_dir

    raise FileNotFoundError(f"Could not find a 'resources' folder starting from {current_file}")
