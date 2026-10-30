"""Keep a planting envelope inside a convex bed without crossing its rail."""
import math


def disk_inside_convex(polygon, x, y, radius):
    if radius < 0 or len(polygon) < 3:
        raise ValueError('Invalid planting envelope')
    edges = list(zip(polygon, polygon[1:] + polygon[:1]))
    area = sum(ax * by - bx * ay for (ax, ay), (bx, by) in edges)
    if abs(area) < 1e-9:
        raise ValueError('Degenerate bed')
    orientation = 1 if area > 0 else -1
    for (ax, ay), (bx, by) in edges:
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-9:
            raise ValueError('Degenerate bed edge')
        inward_distance = orientation * ((bx - ax) * (y - ay) - (by - ay) * (x - ax)) / length
        if inward_distance < radius - 1e-8:
            return False
    return True
