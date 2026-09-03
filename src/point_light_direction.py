import numpy as np


def point_light_direction(light_pos, q):
    """Direction from query point ``q`` toward a point light at ``light_pos``.

    Returns ``(d, max_t)`` where ``d = light_pos - q`` (not normalised, so the
    light is reached at ``t = 1``) and ``max_t = 1.0``.
    """
    # TODO: return the (un-normalised) vector toward the light and max_t = 1.0.
    raise NotImplementedError("Implement point_light_direction")
