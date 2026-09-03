import numpy as np


def sphere_intersect(center, radius, ray, min_t):
    """Intersect a sphere with a ray.

    Returns ``(hit, t, n)``: whether a hit at parametric distance ``t >= min_t``
    exists, the distance, and the unit surface normal at the hit point. When
    there is no hit, returns ``(False, inf, zeros(3))``.
    """
    # TODO: form the quadratic A t^2 + B t + C = 0 for |o + t d - center|^2 = r^2,
    # take the near root, fall back to the far root when inside the sphere,
    # reject hits with t < min_t, and return n = (hit - center) / radius.
    raise NotImplementedError("Implement sphere_intersect")
