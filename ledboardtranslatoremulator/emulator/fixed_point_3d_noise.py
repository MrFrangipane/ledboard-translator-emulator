"""
Translation of fixed point 3D noise algorithm from C++ to Python
"""
from dataclasses import dataclass


@dataclass
class NoiseParams:
    """Equivalent to FixedPoint3DNoise::Params"""
    scale: int = 3
    octaves: int = 1
    min: int = 0
    max: int = 1024


@dataclass
class ComputeInfo:
    """Equivalent to FixedPoint3DNoise::ComputeInfo"""
    min: int = 0
    max: int = 0


class FixedPoint3DNoise:
    """Python port of FixedPoint3DNoise with fixed point calculations preserved"""

    Scale = 1024  # Fixed-point scaling factor
    PrimeX = 501125321
    PrimeY = 1136930381
    PrimeZ = 1720413743

    def __init__(self, seed: int = 0):
        self.seed = seed
        self.scale = 3
        self.octaves = 1
        self.min = 0
        self.max = self.Scale
        self.compute_info = ComputeInfo(0, 0)

        # Initialize gradient table (same as in C++ implementation)
        self.gradients_3d = [
            0, 1, 1, 0, 0, -1, 1, 0, 0, 1, -1, 0, 0, -1, -1, 0,
            1, 0, 1, 0, -1, 0, 1, 0, 1, 0, -1, 0, -1, 0, -1, 0,
            1, 1, 0, 0, -1, 1, 0, 0, 1, -1, 0, 0, -1, -1, 0, 0,
            0, 1, 1, 0, 0, -1, 1, 0, 0, 1, -1, 0, 0, -1, -1, 0,
            1, 0, 1, 0, -1, 0, 1, 0, 1, 0, -1, 0, -1, 0, -1, 0,
            1, 1, 0, 0, -1, 1, 0, 0, 1, -1, 0, 0, -1, -1, 0, 0,
            0, 1, 1, 0, 0, -1, 1, 0, 0, 1, -1, 0, 0, -1, -1, 0,
            1, 0, 1, 0, -1, 0, 1, 0, 1, 0, -1, 0, -1, 0, -1, 0,
            1, 1, 0, 0, -1, 1, 0, 0, 1, -1, 0, 0, -1, -1, 0, 0,
            0, 1, 1, 0, 0, -1, 1, 0, 0, 1, -1, 0, 0, -1, -1, 0,
            1, 0, 1, 0, -1, 0, 1, 0, 1, 0, -1, 0, -1, 0, -1, 0,
            1, 1, 0, 0, -1, 1, 0, 0, 1, -1, 0, 0, -1, -1, 0, 0,
            0, 1, 1, 0, 0, -1, 1, 0, 0, 1, -1, 0, 0, -1, -1, 0,
            1, 0, 1, 0, -1, 0, 1, 0, 1, 0, -1, 0, -1, 0, -1, 0,
            1, 1, 0, 0, -1, 1, 0, 0, 1, -1, 0, 0, -1, -1, 0, 0,
            1, 1, 0, 0, 0, -1, 1, 0, -1, 1, 0, 0, 0, -1, -1, 0
        ]

    def set_params(self, params: NoiseParams):
        self.scale = params.scale
        self.octaves = params.octaves
        self.min = params.min
        self.max = params.max

    def get_params(self) -> NoiseParams:
        return NoiseParams(self.scale, self.octaves, self.min, self.max)

    def get_compute_info(self) -> ComputeInfo:
        return self.compute_info

    def get_value(self, x: int, y: int, z: int) -> int:
        noise = 0
        for i in range(self.octaves):
            octave = 1 << i  # 2^i

            noise_sample = self.get_raw_value(
                self.scale * x * octave,
                self.scale * y * octave,
                self.scale * z
            )
            noise += noise_sample // octave

        # Ensure [0 - Scale] values
        noise = (noise + self.Scale) // 2

        if noise <= self.min:
            return 0
        if noise >= self.max:
            return self.Scale

        noise = (noise - self.min) * self.Scale // (self.max - self.min)

        if noise < self.compute_info.min:
            self.compute_info.min = noise
        if noise > self.compute_info.max:
            self.compute_info.max = noise

        return noise

    def dot_grid_gradient(self, X: int, Y: int, Z: int, x: int, y: int, z: int) -> int:
        gx, gy, gz = self.random_gradient(X, Y, Z)

        dx = x - X
        dy = y - Y
        dz = z - Z

        dot = (dx * gx + dy * gy + dz * gz) // self.Scale

        return dot

    def get_raw_value(self, x: int, y: int, z: int) -> int:
        X0 = (x // self.Scale) * self.Scale
        Y0 = (y // self.Scale) * self.Scale
        Z0 = (z // self.Scale) * self.Scale

        X1 = X0 + self.Scale if x > 0 else X0 - self.Scale
        Y1 = Y0 + self.Scale if y > 0 else Y0 - self.Scale
        Z1 = Z0 + self.Scale if z > 0 else Z0 - self.Scale

        wx = abs(x - X0)
        wy = abs(y - Y0)
        wz = abs(z - Z0)

        # Lower top x 0 0
        n0 = self.dot_grid_gradient(X0, Y0, Z0, x, y, z)
        n1 = self.dot_grid_gradient(X1, Y0, Z0, x, y, z)
        lt = self.linear_interpolate(n0, n1, wx)

        # Lower bottom x 1 0
        n0 = self.dot_grid_gradient(X0, Y1, Z0, x, y, z)
        n1 = self.dot_grid_gradient(X1, Y1, Z0, x, y, z)
        lb = self.linear_interpolate(n0, n1, wx)

        # Lower x y 0
        l = self.linear_interpolate(lt, lb, wy)

        # Upper top x 0 1
        n0 = self.dot_grid_gradient(X0, Y0, Z1, x, y, z)
        n1 = self.dot_grid_gradient(X1, Y0, Z1, x, y, z)
        ut = self.linear_interpolate(n0, n1, wx)

        # Upper bottom x 1 1
        n0 = self.dot_grid_gradient(X0, Y1, Z1, x, y, z)
        n1 = self.dot_grid_gradient(X1, Y1, Z1, x, y, z)
        ub = self.linear_interpolate(n0, n1, wx)

        # Upper x y 1
        u = self.linear_interpolate(ut, ub, wy)

        # Value
        value = self.linear_interpolate(l, u, wz)

        return value

    def random_gradient(self, x: int, y: int, z: int) -> tuple[int, int, int]:
        ix = x // self.Scale
        iy = y // self.Scale
        iz = z // self.Scale

        # Borrowed from FastNoiseLite
        ix *= self.PrimeX
        iy *= self.PrimeY
        iz *= self.PrimeZ

        hash_val = self.seed ^ ix ^ iy ^ iz

        hash_val *= 0x27d4eb2d
        hash_val ^= hash_val >> 15
        hash_val &= 127 << 1

        return (
            self.gradients_3d[hash_val] * self.Scale,
            self.gradients_3d[hash_val | 1] * self.Scale,
            self.gradients_3d[hash_val | 2] * self.Scale
        )

    @staticmethod
    def linear_interpolate(a: int, b: int, w: int) -> int:
        scale = FixedPoint3DNoise.Scale
        return a - (a * w // scale) + (b * w // scale)
