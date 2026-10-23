"""Anatomical child morph: raised hands never inherit head enlargement."""


def child_coordinate(coordinate, offset=(0, 0, 0), *, is_head=False, datum=0):
    x, y, z = coordinate
    z -= datum
    if is_head:
        blend = max(0, min(1, (z - 1.31) / .18))
        width = .60 + blend * .36
        height = .60 * min(z, 1.40) + 1.02 * max(0, z - 1.40)
    else:
        width, height = .60, z * .60
    return x * width + offset[0], y * width + offset[1], height + offset[2]
