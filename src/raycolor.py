import numpy as np

from backend.scene import Ray
from src.first_hit import first_hit
from src.blinn_phong_shading import blinn_phong_shading
from src.reflect import reflect

MAX_RECURSIVE_CALLS = 10


def raycolor(ray, min_t, objects, lights, num_recursive_calls):
    """Recursively trace ``ray`` and return ``(hit, rgb)``.

    Find the first hit; shade it with Blinn-Phong. If the material is mirror-like
    (``max(km) > 0``) and we have not exceeded the recursion cap
    (``MAX_RECURSIVE_CALLS``), trace the reflected ray and add
    ``km * reflected_colour`` (component-wise).

    Returns ``(False, zeros(3))`` when the ray escapes the scene.
    """
    # TODO: first_hit -> blinn_phong_shading; if mirror-like and within the
    # recursion cap, reflect the ray about the normal, recurse, and add the
    # km-weighted reflected colour. Use epsilon = 1e-6 for the reflected ray.
    raise NotImplementedError("Implement raycolor")
