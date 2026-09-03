import numpy as np

from backend.scene import Ray


def viewing_ray(camera, i, j, width, height):
    """Construct the perspective viewing ray through pixel ``(i, j)``.

    Parameters
    ----------
    camera : backend.scene.Camera
    i, j : int
        Row (``i``, from the top) and column (``j``, from the left) of the pixel.
    width, height : int
        Image resolution in pixels.

    Returns
    -------
    backend.scene.Ray
        Ray whose origin is the eye and whose (un-normalised) direction lands on
        the centre of pixel ``(i, j)`` at ``t = 1``.
    """
    # TODO: map the pixel (i, j) to image-plane offsets (u along camera.u,
    # v along camera.v), then build the ray from the eye through that point.
    # Remember +v points up while row index i grows downward.
    raise NotImplementedError("Implement viewing_ray")
