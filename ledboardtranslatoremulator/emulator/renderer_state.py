from dataclasses import dataclass, field


@dataclass
class RendererState:
    """State of the renderer"""
    is_running: bool = False
    z: int = 0
    x: int = 0
    y: int = 0
    runner_led_index: int = 0
    speed_offset_loop_counter: int = 0
    speed_offset: int = 0
    luminance_offset: int = 0
    shutter_elapsed: int = 0
    runners_timestamps: dict[int, int] = field(default_factory=dict)
    previous_millis: int = 0
    fps_frame_count: int = 0
    fps_millis: int = 0
    is_filled_green: bool = False
    has_white: bool = False
