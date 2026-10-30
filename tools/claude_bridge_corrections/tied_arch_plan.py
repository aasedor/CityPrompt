"""One source-specific plan transform for every tied-arch bridge component."""
import math


def trapezoid_plan(x, y, halfspan=23, end_skew_degrees=6, heading_degrees=13):
    """Opposite end skews, rather than a uniform parallelogram shear."""
    if halfspan <= 0 or abs(end_skew_degrees) >= 45:
        raise ValueError('Invalid tied-arch plan dimensions')
    local_x = x * (1 - math.tan(math.radians(end_skew_degrees)) * y / halfspan)
    angle = math.radians(heading_degrees)
    return local_x * math.cos(angle) - y * math.sin(angle), local_x * math.sin(angle) + y * math.cos(angle)
