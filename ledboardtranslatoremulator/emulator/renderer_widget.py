import json
import time

from PySide6.QtCore import QTimer
from PySide6.QtGui import Qt, QPainter, QColor, QBrush
from PySide6.QtWidgets import QWidget

from ledboardlib import SamplingPoint, ControlParameters, InteropDataStore
from ledboardlib.color_mode import ColorMode
from ledboardlib.mapping_mode import MappingMode

from ledboardtranslatoremulator.emulator.fixed_point_3d_noise import FixedPoint3DNoise, NoiseParams
from ledboardtranslatoremulator.emulator.renderer_state import RendererState
from ledboardtranslatoremulator.emulator.sampling_point_bounds import SamplingPointBounds
from pyside6helpers import resources


class LedRendererEmulatorWidget(QWidget):
    """Python port of LedRenderer with QPixmap rendering"""

    def __init__(self):
        super().__init__()

        # Load interop data
        interop_store = InteropDataStore(resources.find_from(__file__, "interop-data-melinerion.json"))

        # Initialize state and objects
        self.ignore_dimmer = True
        self.state = RendererState()
        self.noise = FixedPoint3DNoise()
        self.sampling_points: list[SamplingPoint] = interop_store.data.sampling_points
        self.control_params: ControlParameters | None = interop_store.data.default_control_parameters
        self.bounds = SamplingPointBounds()
        self.gamma_lookup = [0] * 256

        # Compute gamma lookup and bounds
        self.compute_gamma_lookup(2.6)

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

    def compute_gamma_lookup(self, gamma: float):
        """Compute gamma correction lookup table"""
        for i in range(256):
            # Calculate gamma-corrected value
            #corrected = int(pow(i / 255.0, gamma) * 255 + 0.5)
            #self.gamma_lookup[i] = max(0, min(255, corrected))
            # No gamma for Eumulator
            self.gamma_lookup[i] = i

    def set_points(self, points):
        self.sampling_points = points
        self.compute_bounds()

    def set_control_params(self, params: ControlParameters):
        self.control_params = params

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
            octaves=self.control_params.noise_octaves,
            scale=self.control_params.noise_scale,
            min=self.control_params.noise_min,
            max=self.control_params.noise_max,
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

    def paintEvent(self, event):
        rect = event.rect()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(rect, Qt.black)

        if not self.state.is_running or self.control_params is None:
            return

        # Calculate elapsed time
        current_millis = int(time.time() * 1000)
        elapsed = current_millis - self.state.previous_millis
        self.state.previous_millis = current_millis

        # Update FPS counter
        self.state.fps_frame_count += 1
        self.state.fps_millis += elapsed
        if self.state.fps_millis >= 1000:
            fps = self.state.fps_frame_count / (self.state.fps_millis / 1000.0)
            self.setWindowTitle(f"LED Renderer Emulation - {fps:.1f} FPS")
            self.state.fps_frame_count = 0
            self.state.fps_millis = 0

        # Update noise movement
        self.state.z += self.control_params.noise_speed_z
        self.state.x += self.control_params.noise_speed_x
        self.state.y += self.control_params.noise_speed_y

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
        shutter = max(20, 255 - self.control_params.shutter)
        self.state.shutter_elapsed += elapsed
        if self.control_params.shutter > 0:
            if self.state.shutter_elapsed > shutter:
                is_shutter_open = 0
            if self.state.shutter_elapsed > shutter * 2:
                self.state.shutter_elapsed = 0

        # Draw each LED
        for point in self.sampling_points:
            # Single LED mode
            if self.control_params.single_led >= 0:
                if point.index == self.control_params.single_led:
                    brightness = self.control_params.single_led_brightness
                    r, g, b = brightness, brightness, brightness
                else:
                    r, g, b = 0, 0, 0

            # Normal mode with noise
            elif self.control_params.is_noise_on:
                # Get noise value for this point
                x, y = 0, 0
                if self.control_params.mapping_mode == MappingMode.MODE_1D:
                    x = point.index
                    y = 0
                else:
                    x = point.x
                    y = point.y

                noise = self.get_noise_at(
                    x * self.control_params.noise_scale_x + self.state.x,
                    y * self.control_params.noise_scale_y + self.state.y,
                    self.state.z
                )
                # Scale to 0-255
                noise_byte = min(255, max(0, noise * 255 // self.noise.Scale))

                # Apply dimmer
                if not self.ignore_dimmer:
                    brightness = noise_byte * self.control_params.dimmer // 255
                else:
                    brightness = noise_byte

                # Apply color mode
                if self.control_params.color_mode == ColorMode.HSL:
                    # Use HSL values for noise
                    r, g, b = self.hsl_to_rgb(
                        self.control_params.noise_h,
                        self.control_params.noise_s,
                        min(255, max(0, self.control_params.noise_l * brightness // 255))
                    )
                else:  # RGB
                    # Use RGB values for noise, scaled by brightness
                    r = self.control_params.noise_r * brightness // 255
                    g = self.control_params.noise_g * brightness // 255
                    b = self.control_params.noise_b * brightness // 255
            else:
                # No noise mode
                r, g, b = 0, 0, 0

            if not is_shutter_open:
                r, g, b = 0, 0, 0

            # Apply gamma correction
            r = self.gamma_lookup[min(255, max(0, r))]
            g = self.gamma_lookup[min(255, max(0, g))]
            b = self.gamma_lookup[min(255, max(0, b))]

            # Draw the LED
            x = offset_x + (point.x - self.bounds.min_x) * scale
            y = offset_y + (point.y - self.bounds.min_y) * scale

            size = 10

            color = QColor(r, g, b)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)

            # Draw LED
            painter.drawEllipse(x - size / 2, y - size / 2, size, size)

        # End painting
        painter.end()
