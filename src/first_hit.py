import numpy as np

from src.sphere_intersect import sphere_intersect
from src.plane_intersect import plane_intersect
from src.triangle_intersect import triangle_intersect


def _intersect_object(obj, ray, min_t):
    """Dispatch ray-object intersection on the geometry ``kind``.

    Each object's ``geometry`` is one of the dataclasses in ``backend.scene``
    (``Sphere``, ``Plane``, ``Triangle`` or ``Soup``) and carries a ``kind``
    string. A ``Soup`` holds an ``(n, 3, 3)`` array of triangles.
    """
    # TODO: dispatch on obj.geometry.kind to the matching intersection helper;
    # for a "soup" loop over its triangles and keep the closest hit.
    raise NotImplementedError("Implement first_hit (object dispatch)")


def first_hit(ray, min_t, objects):
    """Find the closest object hit by ``ray`` with ``t >= min_t``.

    Returns ``(hit, hit_id, t, n)``: whether anything was hit, the index of the
    closest object, the parametric distance ``t`` and the unit normal ``n`` at
    that hit. When nothing is hit, returns ``(False, -1, inf, zeros(3))``.
    """
    # TODO: loop over objects, intersect each, and keep the one with smallest t.
    raise NotImplementedError("Implement first_hit")
