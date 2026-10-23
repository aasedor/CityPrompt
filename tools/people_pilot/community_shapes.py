"""Small deterministic rest-mesh edits; skeleton attachment landmarks stay fixed."""


def shape_vertex(design, name, coordinate, leg_center=0):
    x, y, z = coordinate
    if 'Hip_length_overshirt' in name:
        influence = max(0, min(1, (1.44 - z) / .25))
        fit = 1 + (design['fit'] - 1) * influence
        x *= fit
        y *= fit
        z -= design['hem'] * max(0, min(1, (1.18 - z) / .295))
    elif 'Straight_trouser' in name:
        influence = max(0, min(1, (.78 - z) / .4))
        fit = 1 + (design['leg_fit'] - 1) * influence
        x = leg_center + (x - leg_center) * fit
        y = .025 + (y - .025) * fit
    # The central head/neck skeleton is preserved; all face, eyes and hair
    # meshes receive the same adjustment so they remain mutually registered.
    if z > 1.51:
        influence = min(1, (z - 1.51) / .10)
        x *= 1 + (design['face_width'] - 1) * influence
    return x, y, z
