import numpy as np


def plane_intersect(point, normal, ray, min_t):
    """Intersect an (infinite) plane with a ray.

    The plane is all ``q`` with ``(q - point) . normal = 0``. Substituting the
    ray and solving for ``t`` gives ``t = -(origin - point).n / (direction.n)``.

    Returns ``(hit, t, n)``; ``(False, inf, zeros(3))`` when there is no hit at
    ``t >= min_t``.
    """
    # TODO: solve for t, reject parallel rays and hits with t < min_t,
    # and return the plane normal as the surface normal.
    raise NotImplementedError("Implement plane_intersect")
