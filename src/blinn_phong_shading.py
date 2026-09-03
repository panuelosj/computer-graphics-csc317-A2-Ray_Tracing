import numpy as np

from backend.scene import Ray, light_direction
from src.first_hit import first_hit


def blinn_phong_shading(ray, hit_id, t, n, objects, lights):
    """Blinn-Phong shaded colour at the hit point of ``ray`` on ``objects[hit_id]``.

    Ambient term ``0.1 * ka`` plus, for each light that is *not* occluded
    (checked with a shadow ray offset by a small epsilon), a diffuse term
    ``kd * I * max(0, n.l)`` and a specular term ``ks * I * max(0, n.h)**p``,
    where ``l`` is the unit direction to the light and ``h`` is the unit
    half-vector ``normalize(l - normalize(ray.direction))``.

    Use ``light_direction(light, q)`` (from ``backend.scene``) to get the
    direction ``d`` toward each light and its parametric distance ``max_t``.

    Returns an RGB ``(3,)`` array (un-clamped).
    """
    # TODO: start from the ambient term, then for each light shoot a shadow ray
    # from the hit point (offset by epsilon) and, if unobstructed up to max_t,
    # add the diffuse and specular contributions.
    raise NotImplementedError("Implement blinn_phong_shading")
