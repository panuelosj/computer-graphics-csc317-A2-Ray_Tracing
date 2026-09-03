import numpy as np


def directional_light_direction(light_dir, q):
    """Direction from query point ``q`` toward a directional light.

    ``light_dir`` points *from* the light *toward* the scene, so the direction
    toward the light is ``-normalize(light_dir)``. The light is infinitely far
    away, so ``max_t = inf``.

    Returns ``(d, max_t)``.
    """
    # TODO: return -normalize(light_dir) and max_t = infinity.
    raise NotImplementedError("Implement directional_light_direction")
