from dataclasses import fields
from importlib import resources
from typing import get_type_hints, get_args

import time

from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import Qt, QPainter, QColor, QBrush
from PySide6.QtWidgets import QWidget

from ledboarddesktop.control_parameters.annotated_dataclass import UiControlParameters

from ledboardlib import SamplingPoint, InteropDataStore, Fixture, ControlParameters
from ledboardlib.color_mode import ColorMode
from ledboardlib.dmx_attribution.c_struct import DmxAttributionStruct
from ledboardlib.mapping_mode import MappingMode

from pythonartnet.broadcaster import ArtnetBroadcaster

from ledboardtranslatoremulator.emulator.fixed_point_3d_noise import FixedPoint3DNoise, NoiseParams
from ledboardtranslatoremulator.emulator.renderer_state import RendererState
from ledboardtranslatoremulator.emulator.sampling_point_bounds import SamplingPointBounds
from ledboardtranslatoremulator.translators.artnet import ArtnetTranslator


class LedRendererEmulatorWidget(QWidget):
    """Python port of LedRenderer with QPixmap rendering"""

    detailsUpdated = Signal(str)

    def __init__(self, broadcaster: ArtnetBroadcaster):
        super().__init__()

        self.fixture: Fixture | None = None
        self.broadcaster = broadcaster

        # Load interop data
        interop_filepath = str(resources.files('ledboardtranslatoremulator.resources') / 'interop-data-elephanz.json')
        interop_data = InteropDataStore(interop_filepath).data

        # Fixture to emulate
        for fixture in interop_data.fixtures:
            if fixture.name.lower() == "elephanz":
                print(f"Fixture for emulation is {fixture}")
                self.artnet_translator = ArtnetTranslator(fixture)
                break

        # Initialize state and objects
        self.bounds = SamplingPointBounds()
        self.control_parameters: ControlParameters | None  = None
        self.ignore_dimmer = interop_data.emulator_ignores_dimmer
        self.noise = FixedPoint3DNoise()
        self.sampling_points: list[SamplingPoint] = interop_data.sampling_points
        print(f"Loaded {len(self.sampling_points)} sampling points from interop data")
        self.state = RendererState()

        # Setup timer for animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)

        # Start rendering
        self.start()

    def start(self):
        """Start the rendering loop"""
        self.compute_bounds()
        self.state.is_running = True
        self.state.previous_millis = int(time.time() * 1000)
        self.timer.start(16)  # ~60 FPS

    def stop(self):
        """Stop the rendering loop"""
        self.state.is_running = False
        self.timer.stop()

    def compute_bounds(self):
        """Compute min/mid/max bounds for all sampling points"""
        if not self.sampling_points:
            return

        # Find min/max x/y
        self.bounds.min_x = min(point.x for point in self.sampling_points)
        self.bounds.max_x = max(point.x for point in self.sampling_points)
        self.bounds.min_y = min(point.y for point in self.sampling_points)
        self.bounds.max_y = max(point.y for point in self.sampling_points)

        # Calculate mid points
        self.bounds.mid_x = (self.bounds.min_x + self.bounds.max_x) // 2
        self.bounds.mid_y = (self.bounds.min_y + self.bounds.max_y) // 2

    def get_noise_at(self, x: int, y: int, z: int) -> int:
        """Get noise value at given coordinates"""
        self.noise.set_params(NoiseParams(
            octaves=self.control_parameters.noise_octaves,
            scale=self.control_parameters.noise_scale,
            min=self.control_parameters.noise_min,
            max=self.control_parameters.noise_max,
        ))
        return self.noise.get_value(x, y, z)

    @staticmethod
    def hsl_to_rgb(h: int, s: int, l: int) -> tuple[int, int, int]:
        """Convert HSL to RGB (all values 0-255)"""
        h = (h % 256) / 255.0 * 360.0
        s = s / 255.0
        l = l / 255.0

        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2

        r, g, b = 0, 0, 0

        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        elif 300 <= h < 360:
            r, g, b = c, 0, x

        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)

        return r, g, b

    def update_details(self):
        lines: list[str] = [f"{self.state.fps:.1f} FPS"]
        ui_annotations = {
            name: get_args(annotation)[1] for name, annotation in get_type_hints(UiControlParameters, include_extras=True).items()
        }

        for attribution in sorted(fields(DmxAttributionStruct), key=lambda x: x.default):
            if attribution.default != 0:
                pretty_name = ui_annotations[attribution.name].label
                value = getattr(self.control_parameters, attribution.name)
                lines.append(f"{attribution.default:02d} {pretty_name}: {value}")

        self.detailsUpdated.emit("\n".join(lines))

    def paintEvent(self, event):
        self.control_parameters = self.artnet_translator.translate(bytearray(self.broadcaster.universes[0].buffer))
        
        rect = event.rect()
        painter = QPainter(self)
        painter.fillRect(rect, Qt.black)

        if not self.state.is_running:
            return

        # Calculate elapsed time
        current_millis = int(time.time() * 1000)
        elapsed = current_millis - self.state.previous_millis
        self.state.previous_millis = current_millis

        # Update noise movement
        self.state.x += int(elapsed * self.control_parameters.noise_speed_x / 10)
        self.state.y += int(elapsed * self.control_parameters.noise_speed_y / 10)
        self.state.z += int(elapsed * self.control_parameters.noise_speed_z / 10)

        # Calculate scaling to fit the window
        view_width = self.width()
        view_height = self.height()

        # Calculate aspect ratio of bounds
        bounds_width = self.bounds.max_x - self.bounds.min_x
        bounds_height = self.bounds.max_y - self.bounds.min_y

        # Determine scale and offset to fit in view
        scale_x = view_width / max(1, bounds_width)
        scale_y = view_height / max(1, bounds_height)
        scale = min(scale_x, scale_y) * 0.9  # 90% of available space

        # Center the visualization
        offset_x = (view_width - bounds_width * scale) / 2
        offset_y = (view_height - bounds_height * scale) / 2

        # Apply shutter effect
        is_shutter_open = 1
        shutter = max(20, 255 - self.control_parameters.shutter)
        self.state.shutter_elapsed += elapsed
        if self.control_parameters.shutter > 0:
            if self.state.shutter_elapsed > shutter:
                is_shutter_open = 0
            if self.state.shutter_elapsed > shutter * 2:
                self.state.shutter_elapsed = 0

        # Draw each LED
        for point in self.sampling_points:
            brightness = 0

            # Single LED mode
            if self.control_parameters.single_led >= 0:
                if point.index == self.control_parameters.single_led:
                    brightness = self.control_parameters.single_led_brightness
                    r, g, b = brightness, brightness, brightness
                else:
                    r, g, b = 0, 0, 0

            # Noise ON
            elif self.control_parameters.is_noise_on:
                # Get noise value for this point
                x, y = 0, 0
                if self.control_parameters.mapping_mode == MappingMode.MODE_1D:
                    x = point.index
                    y = 0
                else:
                    x = point.x
                    y = point.y

                noise = self.get_noise_at(
                    x * self.control_parameters.noise_scale_x + self.state.x,
                    y * self.control_parameters.noise_scale_y + self.state.y,
                    self.state.z
                )
                noise_byte = noise * 255 / self.noise.Scale

                # Apply dimmer
                if not self.ignore_dimmer:
                    brightness = noise_byte * self.control_parameters.dimmer / 255
                else:
                    brightness = noise_byte

                # Apply color mode
                if self.control_parameters.color_mode == ColorMode.HSL_DIMMER:
                    # Use HSL values for noise
                    r, g, b = self.hsl_to_rgb(
                        self.control_parameters.noise_h,
                        self.control_parameters.noise_s,
                        self.control_parameters.noise_l
                    )
                else:
                    # Use RGB values for noise, scaled by brightness
                    r = self.control_parameters.noise_r
                    g = self.control_parameters.noise_g
                    b = self.control_parameters.noise_b
            else:
                # Noise OFF
                r, g, b = 0, 0, 0

            if not is_shutter_open:
                r, g, b = 0, 0, 0

            r = r * brightness / 255
            g = g * brightness / 255
            b = b * brightness / 255

            # Draw the LED
            x = offset_x + (point.x - self.bounds.min_x) * scale
            y = offset_y + (point.y - self.bounds.min_y) * scale

            color = QColor(r, g, b)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)

            # Draw LED
            painter.drawEllipse(x - scale / 2, y - scale / 2, scale, scale)

        # End painting
        painter.end()

        # Update FPS counter
        self.state.fps_frame_count += 1
        self.state.fps_millis += elapsed
        if self.state.fps_millis >= 500:
            self.state.fps = self.state.fps_frame_count / (self.state.fps_millis / 500.0)
            self.state.fps_frame_count = 0
            self.state.fps_millis = 0

        self.update_details()