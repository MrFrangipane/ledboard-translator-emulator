from dataclasses import dataclass


@dataclass
class SamplingPointBounds:
    """Bounds for sampling points"""
    min_x: int = 0
    mid_x: int = 0
    max_x: int = 0
    min_y: int = 0
    mid_y: int = 0
    max_y: int = 0
