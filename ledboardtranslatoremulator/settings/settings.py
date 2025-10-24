from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class EmulatorSettings():
    always_on_top: bool = False
    show_details: bool = True
    target_ip: str | None = None
