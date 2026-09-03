"""Optional soup acceleration, hidden behind the scene API.

Why a mesh scene is slow
------------------------
``first_hit`` intersects a soup by testing every triangle, one call at a time.
That is the honest algorithm and it is what you are graded on. The trouble is
that a single ray-triangle test in Python costs roughly 3 microseconds -- not
because the arithmetic is hard, but because it runs on numpy *scalars*, where
every operation pays dispatch overhead a compiled language does not. The same
test in an optimised compiled language takes tens of nanoseconds.

``bunny.json`` makes that gap hurt: it has 4 lights and mirror-ish materials,
so every pixel triggers 1 primary hit plus 10 mirror bounces, each casting 4
shadow rays -- **55 full scene traversals per pixel**, about 55,000 triangle
tests. At 3 us each that is roughly twelve hours for a 640x360 frame. Nothing
is recomputed needlessly: the work measures at exactly 55 x 1000, the
algorithm's own minimum.

How this speeds it up
---------------------
numpy is not slow -- it is slow *per call*. Testing one 3-vector at a time is
the worst way to use it; testing a thousand at once is the best. So the backend
does the bulk work in a single vectorised pass:

* ``Ray`` is a backend class and every ray -- camera, shadow, mirror -- is
  constructed through it, so wrapping its constructor reveals which ray is
  being traced.
* Your ``first_hit`` only reads ``geometry.kind`` and ``geometry.triangles``,
  so a soup can run one vectorised slab test over all of its triangle bounding
  boxes at once and hand back only the few the ray could possibly hit.

Vectorised, that test costs about **20 nanoseconds per triangle** -- roughly
160x less than the 3 microseconds the same triangle costs inside the scalar
loop, and finally in the same league as compiled code. Your loop then runs
over a handful
of triangles instead of a thousand.

Why the result is identical, not approximate
--------------------------------------------
A triangle the ray truly hits contains the hit point, and that point lies
inside the triangle's bounding box -- so a ray that hits the triangle must also
cross its box. Culling on boxes can only ever discard triangles that were going
to miss anyway.

When it is used
---------------
A scene opts in with ``"accelerate": true`` at the top level of its ``.json``
(only ``bunny`` and ``mirror`` do); ``--accel`` / ``--no-accel`` override it for
a single run. **Grading never enables it**, so your mark always reflects the
honest brute-force path -- and building an acceleration structure yourself,
rather than being handed one, is the next assignment.

The one assumption is that the ray being traced is the most recently
constructed one, which holds when a ray is built and passed straight to
``first_hit``, as the stubs do. If your code batches rays differently, use
``--no-accel``; it cannot affect your marks either way.
"""

from __future__ import annotations

import numpy as np

from .scene import Ray

# The ray currently being traced, recorded as it is constructed.
_CURRENT_RAY = [None]
_HOOK_INSTALLED = [False]

# Stand-in for 1/0 so a ray parallel to an axis needs no special case: the
# slab test then yields +-inf, which compares correctly.
_TINY = 1e-300

_EMPTY = np.empty((0, 3, 3), dtype=float)


def install_ray_hook() -> None:
    """Make every ``Ray`` record itself as the one being traced."""
    if _HOOK_INSTALLED[0]:
        return
    original_init = Ray.__init__

    def tracking_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        _CURRENT_RAY[0] = self

    Ray.__init__ = tracking_init
    _HOOK_INSTALLED[0] = True


class AcceleratedSoup:
    """A triangle soup that returns only the triangles a ray could hit.

    Duck-types :class:`backend.scene.Soup`: it exposes ``kind`` and
    ``triangles``, which is all ``first_hit`` ever reads.
    """

    kind = "soup"

    def __init__(self, triangles):
        self._tris = np.ascontiguousarray(np.asarray(triangles, dtype=float))
        lo = self._tris.min(axis=1)
        hi = self._tris.max(axis=1)
        # Column-major (3, N): three contiguous runs let each axis of the slab
        # test be one clean vector op. Measured ~2.8x faster than (N, 3).
        self._lo = np.ascontiguousarray(lo.T)
        self._hi = np.ascontiguousarray(hi.T)
        self._near = np.empty(len(self._tris), dtype=float)
        self._far = np.empty(len(self._tris), dtype=float)
        self.queries = 0
        self.returned = 0

    def _candidates(self, origin, direction):
        """Indices of triangles whose bounding box this ray crosses."""
        inv = 1.0 / np.where(direction == 0.0, _TINY, direction)
        near, far = self._near, self._far
        for axis in range(3):
            a = (self._lo[axis] - origin[axis]) * inv[axis]
            b = (self._hi[axis] - origin[axis]) * inv[axis]
            lo_a = np.minimum(a, b)
            hi_a = np.maximum(a, b)
            if axis == 0:
                near[:] = lo_a
                far[:] = hi_a
            else:
                np.maximum(near, lo_a, out=near)
                np.minimum(far, hi_a, out=far)
        np.maximum(near, 0.0, out=near)
        return np.flatnonzero(far >= near)

    @property
    def triangles(self):
        ray = _CURRENT_RAY[0]
        if ray is None:                      # nothing traced yet: be safe
            return self._tris
        origin = np.asarray(ray.origin, dtype=float)
        direction = np.asarray(ray.direction, dtype=float)
        idx = self._candidates(origin, direction)
        self.queries += 1
        self.returned += len(idx)
        if len(idx) == 0:
            return _EMPTY
        return self._tris[idx]

    @property
    def n_triangles(self):
        return len(self._tris)

    @property
    def mean_tested(self):
        return self.returned / self.queries if self.queries else 0.0


def accelerate(objects) -> list:
    """Replace every soup in ``objects`` with an accelerated equivalent.

    Returns the accelerated soups (for reporting). A no-op for scenes with no
    soup, so it is always safe to call.
    """
    install_ray_hook()
    accelerated = []
    for obj in objects:
        geometry = getattr(obj, "geometry", None)
        if getattr(geometry, "kind", None) == "soup":
            obj.geometry = AcceleratedSoup(geometry.triangles)
            accelerated.append(obj.geometry)
    return accelerated


def describe(soups) -> str:
    """A one-line summary of how much work was avoided."""
    if not soups:
        return "  acceleration: no triangle soups in this scene, nothing to do"
    total = sum(s.n_triangles for s in soups)
    tested = sum(s.mean_tested for s in soups)
    if tested <= 0:
        return f"  acceleration: {len(soups)} soup(s), {total} triangles"
    return (f"  acceleration: your first_hit saw {tested:.1f} of {total} "
            f"triangles per ray ({total / tested:.0f}x fewer tests)")
