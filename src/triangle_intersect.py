import numpy as np


def triangle_intersect(a, b, c, ray, min_t):
    """Intersect a triangle ``(a, b, c)`` with a ray.

    Solves ``e + t*d = a + beta*(b-a) + gamma*(c-a)`` (Cramer's rule, following
    Marschner & Shirley). A hit requires ``beta >= 0``, ``gamma >= 0``,
    ``beta + gamma <= 1`` and ``t >= min_t``.

    Returns ``(hit, t, n)`` with ``n`` the unit normal ``norm((a-b) x (a-c))``;
    ``(False, inf, zeros(3))`` when there is no valid hit.
    """
    # TODO: solve the 3x3 system for (t, beta, gamma) with Cramer's rule,
    # apply the barycentric tests, and compute the unit normal.
    raise NotImplementedError("Implement triangle_intersect")
