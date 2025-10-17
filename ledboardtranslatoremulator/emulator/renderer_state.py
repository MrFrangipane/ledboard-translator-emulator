from dataclasses import dataclass


@dataclass
class RendererState:
    """State of the renderer"""
    fps: float = 0.0
    fps_frame_count: int = 0
    fps_millis: int = 0

    is_running: bool = False
    previous_millis: int = 0

    shutter_elapsed: int = 0

    x: int = 0
    y: int = 0
    z: int = 0
