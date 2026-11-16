"""Blender-free hard-surface primitives for the Calgary detail kit.

Metres, Z-up, authored about a ground origin that becomes the placement anchor.
Everything lands in the same flat-shaded linear vertex-colour soup the prairie
foliage uses, so one matte mesh (plus an optional smoother glass/ice mesh)
carries a whole object and the shared instanced renderer needs no changes.
"""
from contextlib import contextmanager
import math
import random

import build_local_foliage as foliage


def _matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _transform(x, y, z, yaw, pitch, roll, scale):
    cz, sz = math.cos(yaw), math.sin(yaw)
    cy, sy = math.cos(pitch), math.sin(pitch)
    cx, sx = math.cos(roll), math.sin(roll)
    # yaw about Z, then pitch about Y, then roll about X
    r = [[cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
         [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
         [-sy, cy * sx, cy * cx]]
    return [[r[0][0] * scale, r[0][1] * scale, r[0][2] * scale, x],
            [r[1][0] * scale, r[1][1] * scale, r[1][2] * scale, y],
            [r[2][0] * scale, r[2][1] * scale, r[2][2] * scale, z],
            [0, 0, 0, 1]]


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, f):
    return (a[0] * f, a[1] * f, a[2] * f)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(a):
    length = math.sqrt(dot(a, a))
    return (a[0] / length, a[1] / length, a[2] / length) if length > 1e-12 else (0.0, 0.0, 1.0)


def mix(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def rounded_rect(length, width, radius, steps=5):
    """Counter-clockwise outline of a rounded rectangle centred on the origin."""
    radius = min(radius, length / 2, width / 2)
    points = []
    for cx, cy, start in ((length / 2 - radius, width / 2 - radius, 0), (-length / 2 + radius, width / 2 - radius, math.pi / 2),
                          (-length / 2 + radius, -width / 2 + radius, math.pi), (length / 2 - radius, -width / 2 + radius, 3 * math.pi / 2)):
        for i in range(steps + 1):
            a = start + (math.pi / 2) * i / steps
            points.append((cx + math.cos(a) * radius, cy + math.sin(a) * radius))
    return points


class Solid:
    def __init__(self, seed=1):
        self.rng = random.Random(seed)
        self.random = self.rng.random
        self.body = foliage.Part('body')
        self.gloss = foliage.Part('gloss')
        self.gloss.material = 1
        self._stack = [None]
        self._linear = {}

    # --- colour ---------------------------------------------------------
    def c(self, colour, jitter=0.0):
        if isinstance(colour, str):
            if colour not in self._linear:
                self._linear[colour] = foliage.srgb_to_linear(colour)
            colour = self._linear[colour]
        if jitter:
            f = 1 + (self.random() - .5) * 2 * jitter
            colour = tuple(min(1.0, max(0.0, v * f)) for v in colour)
        return colour

    def pick(self, palette, jitter=0.0):
        return self.c(palette[int(self.random() * len(palette))], jitter)

    # --- transforms -----------------------------------------------------
    @contextmanager
    def at(self, x=0.0, y=0.0, z=0.0, yaw=0.0, pitch=0.0, roll=0.0, scale=1.0):
        local = _transform(x, y, z, yaw, pitch, roll, scale)
        self._stack.append(local if self._stack[-1] is None else _matmul(self._stack[-1], local))
        try:
            yield self
        finally:
            self._stack.pop()

    def _p(self, p):
        m = self._stack[-1]
        if m is None:
            return p
        x, y, z = p
        return (m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3], m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3],
                m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3])

    # --- faces ------------------------------------------------------------
    def tri(self, a, b, c, colour, gloss=False):
        (self.gloss if gloss else self.body).triangle(self._p(a), self._p(b), self._p(c), self.c(colour))

    def quad(self, a, b, c, d, colour, gloss=False):
        colour = self.c(colour)
        self.tri(a, b, c, colour, gloss)
        self.tri(a, c, d, colour, gloss)

    def poly(self, points, colour, gloss=False):
        """Convex or star-shaped polygon as a fan about its centroid."""
        n = len(points)
        centre = tuple(sum(p[i] for p in points) / n for i in range(3))
        colour = self.c(colour)
        for i in range(n):
            self.tri(centre, points[i], points[(i + 1) % n], colour, gloss)

    # --- solids -----------------------------------------------------------
    def box(self, centre, size, colour, gloss=False, jitter=0.0, top=None, yaw=0.0):
        if yaw:
            with self.at(centre[0], centre[1], centre[2], yaw=yaw):
                self.box((0, 0, 0), size, colour, gloss, jitter, top)
            return
        x, y, z = centre
        w, d, h = size[0] / 2, size[1] / 2, size[2] / 2
        v = [(x + a * w, y + b * d, z + c * h) for c in (-1, 1) for b in (-1, 1) for a in (-1, 1)]
        colour = self.c(colour, jitter)
        for face in ((0, 2, 3, 1), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)):
            self.quad(v[face[0]], v[face[1]], v[face[2]], v[face[3]], colour, gloss)
        self.quad(v[4], v[5], v[7], v[6], self.c(top) if top else colour, gloss)

    def banded_box(self, centre, size, bands, colour, jitter=.06, top=None):
        """Four walls in horizontal courses with slight tone shifts: siding, logs, shingles."""
        x, y, z = centre
        w, d, h = size[0] / 2, size[1] / 2, size[2]
        for i in range(bands):
            z0, z1 = z + h * i / bands, z + h * (i + 1) / bands
            tone = self.c(colour, jitter)
            ring = [(x - w, y - d), (x + w, y - d), (x + w, y + d), (x - w, y + d)]
            for k in range(4):
                a, b = ring[k], ring[(k + 1) % 4]
                self.quad((a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1), tone)
        self.quad((x - w, y - d, z + h), (x + w, y - d, z + h), (x + w, y + d, z + h), (x - w, y + d, z + h), top or colour)

    def cyl(self, a, b, r0, colour, r1=None, sides=12, cap0=True, cap1=True, gloss=False, jitter=0.0):
        r1 = r0 if r1 is None else r1
        axis = sub(b, a)
        if dot(axis, axis) < 1e-12:
            return
        axis = norm(axis)
        up = (1.0, 0.0, 0.0) if abs(axis[2]) > .95 else (0.0, 0.0, 1.0)
        u = norm(cross(up, axis))
        v = cross(axis, u)
        colour = self.c(colour, jitter)

        def ring(p, r, i):
            ang = i * math.tau / sides
            return (p[0] + r * (u[0] * math.cos(ang) + v[0] * math.sin(ang)), p[1] + r * (u[1] * math.cos(ang) + v[1] * math.sin(ang)),
                    p[2] + r * (u[2] * math.cos(ang) + v[2] * math.sin(ang)))

        for i in range(sides):
            p, q, r, s = ring(a, r0, i), ring(a, r0, i + 1), ring(b, r1, i + 1), ring(b, r1, i)
            self.quad(p, q, r, s, colour, gloss)
            if cap0 and r0 > 0:
                self.tri(a, q, p, colour, gloss)
            if cap1 and r1 > 0:
                self.tri(b, s, r, colour, gloss)

    def tube(self, points, radius, colour, sides=6, gloss=False):
        for a, b in zip(points, points[1:]):
            self.cyl(a, b, radius, colour, sides=sides, cap0=False, cap1=False, gloss=gloss)

    def disc(self, centre, radius, colour, sides=24, gloss=False):
        colour = self.c(colour)
        for i in range(sides):
            a0, a1 = i * math.tau / sides, (i + 1) * math.tau / sides
            self.tri(centre, (centre[0] + math.cos(a0) * radius, centre[1] + math.sin(a0) * radius, centre[2]),
                     (centre[0] + math.cos(a1) * radius, centre[1] + math.sin(a1) * radius, centre[2]), colour, gloss)

    def annulus(self, centre, inner, outer, colour, sides=24, start=0.0, sweep=math.tau, gloss=False):
        colour = self.c(colour)
        for i in range(sides):
            a0, a1 = start + sweep * i / sides, start + sweep * (i + 1) / sides
            p = [(centre[0] + math.cos(a) * r, centre[1] + math.sin(a) * r, centre[2]) for a, r in ((a0, inner), (a0, outer), (a1, outer), (a1, inner))]
            self.quad(p[0], p[1], p[2], p[3], colour, gloss)

    def prism(self, outline, z0, z1, colour, top=None, gloss=False, bottom=False):
        """Extrude a counter-clockwise XY outline between two heights."""
        n = len(outline)
        colour = self.c(colour)
        for i in range(n):
            a, b = outline[i], outline[(i + 1) % n]
            self.quad((a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1), colour, gloss)
        self.poly([(p[0], p[1], z1) for p in outline], top or colour, gloss)
        if bottom:
            self.poly([(p[0], p[1], z0) for p in reversed(outline)], colour, gloss)

    def loft(self, rings, colour, cap_start=True, cap_end=True, gloss=False):
        """Skin consecutive closed rings of equal point count. colour may be f(ring, index)."""
        count = len(rings[0])
        for r in range(len(rings) - 1):
            for i in range(count):
                tone = colour(r, i) if callable(colour) else colour
                j = (i + 1) % count
                self.quad(rings[r][i], rings[r][j], rings[r + 1][j], rings[r + 1][i], tone, gloss)
        if cap_start:
            self.poly(list(reversed(rings[0])), colour(0, 0) if callable(colour) else colour, gloss)
        if cap_end:
            self.poly(rings[-1], colour(len(rings) - 2, 0) if callable(colour) else colour, gloss)

    def torus(self, centre, major, minor, colour, nu=20, nv=8, axis='z'):
        """colour may be f(u_index). axis names the direction the hole faces."""
        def point(i, j):
            a, b = i * math.tau / nu, j * math.tau / nv
            r = major + minor * math.cos(b)
            x, y, z = r * math.cos(a), r * math.sin(a), minor * math.sin(b)
            if axis == 'y':
                x, y, z = x, z, y
            elif axis == 'x':
                x, y, z = z, x, y
            return (centre[0] + x, centre[1] + y, centre[2] + z)

        for i in range(nu):
            tone = colour(i) if callable(colour) else colour
            for j in range(nv):
                self.quad(point(i, j), point(i + 1, j), point(i + 1, j + 1), point(i, j + 1), tone)

    def dome(self, centre, radii, colour, nu=12, nv=6, noise=0.0, full=False):
        """Ellipsoid (full) or its upper half, optionally lumpy. colour may be f(v, u)."""
        offsets = {}

        def point(i, j):
            i %= nu
            if j == nv:
                i = 0
            key = (i, j)
            if key not in offsets:
                offsets[key] = 1 + (self.random() - .5) * 2 * noise
            a = i * math.tau / nu
            b = (j / nv) * (math.pi / 2) if not full else -math.pi / 2 + (j / nv) * math.pi
            f = offsets[key]
            return (centre[0] + radii[0] * math.cos(b) * math.cos(a) * f, centre[1] + radii[1] * math.cos(b) * math.sin(a) * f,
                    centre[2] + radii[2] * math.sin(b) * f)

        for j in range(nv):
            for i in range(nu):
                tone = colour(j, i) if callable(colour) else colour
                if j == nv - 1:
                    self.tri(point(i, j), point(i + 1, j), point(0, nv), tone)
                elif full and j == 0:
                    self.tri(point(0, 0), point(i + 1, 1), point(i, 1), tone)
                else:
                    self.quad(point(i, j), point(i + 1, j), point(i + 1, j + 1), point(i, j + 1), tone)

    # --- wire and mesh ------------------------------------------------------
    def ribbon(self, a, b, width, colour, normal=(0.0, 0.0, 1.0), gloss=False):
        """Flat strip lying in the plane whose normal is given."""
        side = mul(norm(cross(sub(b, a), normal)), width / 2)
        self.quad(sub(a, side), add(a, side), add(b, side), sub(b, side), colour, gloss)

    def net_quad(self, a, b, c, d, nu, nv, width, colour):
        """Square-ish netting across an arbitrary quad a-b-c-d by bilinear lines."""
        normal = norm(cross(sub(b, a), sub(d, a)))
        for i in range(nu + 1):
            t = i / nu
            self.ribbon(mix(a, b, t), mix(d, c, t), width, colour, normal)
        for j in range(nv + 1):
            t = j / nv
            self.ribbon(mix(a, d, t), mix(b, c, t), width, colour, normal)

    def diamond_mesh(self, origin, u, v, spacing, width, colour):
        """Chain-link diagonals across the rectangle origin + s*u + t*v, 0 <= s,t <= 1."""
        lu, lv = math.sqrt(dot(u, u)), math.sqrt(dot(v, v))
        eu, ev = norm(u), norm(v)
        normal = norm(cross(u, v))
        k = -int(lv / spacing) - 1
        while k * spacing < lu:
            for sign in (1, -1):
                # line s = k*spacing + sign*t, with t from 0 to lv, clipped to 0 <= s <= lu
                base = k * spacing if sign == 1 else k * spacing + lv
                t0 = max(0.0, (0 - base) / sign) if sign == 1 else max(0.0, (base - lu))
                t1 = min(lv, (lu - base) / sign) if sign == 1 else min(lv, base)
                if t1 - t0 > 1e-6:
                    p = add(origin, add(mul(eu, base + sign * t0), mul(ev, t0)))
                    q = add(origin, add(mul(eu, base + sign * t1), mul(ev, t1)))
                    self.ribbon(p, q, width, colour, normal)
            k += 1

    def wire(self, a, b, sag, radius, colour, segments=8):
        """A conductor hanging between two points with the given mid-span sag."""
        points = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t - sag * 4 * t * (1 - t))
                  for t in (i / segments for i in range(segments + 1))]
        for p, q in zip(points, points[1:]):
            self.cyl(p, q, radius, colour, sides=3, cap0=False, cap1=False)

    # --- rock ---------------------------------------------------------------
    def rock(self, size, cuts, palette, depth=(.72, .95), jitter=.05, origin=(0.0, 0.0, 0.0), yaw=0.0, top_light=1.08):
        """Angular boulder or quarried block: a box clipped by random planes, flat base on the ground."""
        faces = []
        corners = [(a, b, c) for c in (-1.0, 1.0) for b in (-1.0, 1.0) for a in (-1.0, 1.0)]
        for f in ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)):
            faces.append([corners[i] for i in f])
        for _ in range(cuts):
            n = norm((self.random() * 2 - 1, self.random() * 2 - 1, self.random() * 1.6 - .5))
            support = abs(n[0]) + abs(n[1]) + abs(n[2])
            d = support * (depth[0] + self.random() * (depth[1] - depth[0]))
            kept, cap = [], []
            for face in faces:
                out = []
                for i, p in enumerate(face):
                    q = face[(i + 1) % len(face)]
                    dp, dq = dot(n, p) - d, dot(n, q) - d
                    if dp <= 0:
                        out.append(p)
                    if (dp < 0 < dq) or (dq < 0 < dp):
                        hit = mix(p, q, dp / (dp - dq))
                        out.append(hit)
                        cap.append(hit)
                if len(out) >= 3:
                    kept.append(out)
            unique = []
            for p in cap:
                if all(dot(sub(p, q), sub(p, q)) > 1e-10 for q in unique):
                    unique.append(p)
            if len(unique) >= 3:
                centre = tuple(sum(p[i] for p in unique) / len(unique) for i in range(3))
                e1 = norm(cross(n, (0.0, 0.0, 1.0) if abs(n[2]) < .9 else (1.0, 0.0, 0.0)))
                e2 = cross(n, e1)
                unique.sort(key=lambda p: math.atan2(dot(sub(p, centre), e2), dot(sub(p, centre), e1)))
                kept.append(unique)
            faces = kept
        with self.at(origin[0], origin[1], origin[2], yaw=yaw):
            for face in faces:
                pts = [(p[0] * size[0] / 2, p[1] * size[1] / 2, (p[2] + 1) * size[2] / 2) for p in face]
                normal = norm(cross(sub(pts[1], pts[0]), sub(pts[2], pts[0])))
                tone = self.pick(palette, jitter)
                if abs(normal[2]) > .7:
                    tone = tuple(min(1.0, v * top_light) for v in tone)
                self.poly(pts, tone)
