"""Scene representation and I/O for the ray tracer (non-graded infrastructure).

Everything a student's ``src/`` function receives is built here:

* :class:`Ray` - an origin and a (not-necessarily-unit) direction. A ray is the
  parametric line ``r(t) = origin + t * direction``.
* :class:`Camera` - a pinhole/perspective camera given by its eye ``e``, an
  orthonormal frame ``u`` (right), ``v`` (up), ``w`` (so that ``-w`` looks into
  the scene), the image-plane distance ``d`` (focal length) and the image-plane
  ``width``/``height`` measured in *scene* units.
* :class:`Material` - Blinn-Phong coefficients (ambient ``ka``, diffuse ``kd``,
  specular ``ks``, mirror ``km`` and the ``phong_exponent``).
* geometry dataclasses :class:`Sphere`, :class:`Plane`, :class:`Triangle`,
  :class:`Soup` (a triangle soup), each carrying a ``kind`` string so student
  code can dispatch without importing types.
* :class:`Object` - a geometry plus the material it is painted with.
* :class:`PointLight` / :class:`DirectionalLight` - light sources with colour
  ``I``.

It also exposes :func:`load_scene` (JSON loader for the scene format
assignment) and the two render loops used by ``main.py`` and the tests.
"""

from __future__ import annotations

import json
import os
import struct
from dataclasses import dataclass, field
from typing import List

import numpy as np


# --------------------------------------------------------------------------- #
# Core dataclasses
# --------------------------------------------------------------------------- #
@dataclass
class Ray:
    """A ray ``origin + t * direction``.

    ``direction`` is intentionally *not* normalised: scaling it lets ``t = 1``
    land on a useful point (e.g. the image plane for a viewing ray).
    """

    origin: np.ndarray
    direction: np.ndarray


@dataclass
class Camera:
    eye: np.ndarray          # 3D eye / origin "e"
    u: np.ndarray            # right
    v: np.ndarray            # up
    w: np.ndarray            # -w is the viewing direction
    d: float                 # image-plane distance / focal length
    width: float             # image-plane width  (scene units)
    height: float            # image-plane height (scene units)


@dataclass
class Material:
    ka: np.ndarray           # ambient colour
    kd: np.ndarray           # diffuse colour
    ks: np.ndarray           # specular colour
    km: np.ndarray           # mirror colour
    phong_exponent: float


# --- geometry --------------------------------------------------------------- #
@dataclass
class Sphere:
    center: np.ndarray
    radius: float
    kind: str = "sphere"


@dataclass
class Plane:
    point: np.ndarray
    normal: np.ndarray
    kind: str = "plane"


@dataclass
class Triangle:
    a: np.ndarray
    b: np.ndarray
    c: np.ndarray
    kind: str = "triangle"


@dataclass
class Soup:
    # (n, 3, 3) array: triangles[k] = [a, b, c]
    triangles: np.ndarray
    kind: str = "soup"


@dataclass
class Object:
    geometry: object         # one of Sphere / Plane / Triangle / Soup
    material: Material


# --- lights ----------------------------------------------------------------- #
@dataclass
class PointLight:
    position: np.ndarray
    I: np.ndarray            # colour / intensity
    kind: str = "point"


@dataclass
class DirectionalLight:
    direction: np.ndarray    # direction *from* the light toward the scene
    I: np.ndarray
    kind: str = "directional"


# --------------------------------------------------------------------------- #
# Light-direction dispatch (non-graded helper used by blinn_phong_shading)
# --------------------------------------------------------------------------- #
def light_direction(light, q):
    """Return ``(d, max_t)``: direction from ``q`` *toward* ``light`` and the
    parametric distance to it along ``d`` (``inf`` for a directional light).

    This mirrors the graded ``point_light_direction`` /
    ``directional_light_direction`` functions but lives in the backend so the
    shading code can dispatch on the light type.
    """
    q = np.asarray(q, dtype=float)
    if light.kind == "point":
        return np.asarray(light.position, dtype=float) - q, 1.0
    if light.kind == "directional":
        d = np.asarray(light.direction, dtype=float)
        return -d / np.linalg.norm(d), float("inf")
    raise ValueError(f"unknown light kind {light.kind!r}")


# --------------------------------------------------------------------------- #
# STL reader (binary + ASCII) -> (n, 3, 3) triangle array
# --------------------------------------------------------------------------- #
# Scene-level settings that are not geometry. Kept separate from load_scene so
# its (camera, objects, lights) signature -- which the unit checks rely on --
# does not change.
SCENE_DEFAULTS = {
    # Build a bounding-volume hierarchy over this scene's triangle soups.
    # Off unless a scene asks for it; see backend/accel.py.
    "accelerate": False,
}


def load_scene_settings(path):
    """Read the non-geometry settings of a scene file.

    Returns a dict with :data:`SCENE_DEFAULTS` filled in for anything the file
    does not mention, so callers can read keys unconditionally.
    """
    import json as _json
    with open(path) as f:
        raw = _json.load(f)
    settings = dict(SCENE_DEFAULTS)
    for key in SCENE_DEFAULTS:
        if key in raw:
            settings[key] = raw[key]
    settings["accelerate"] = bool(settings["accelerate"])
    return settings


def read_stl(path):
    """Read an STL file (binary or ASCII) into an ``(n, 3, 3)`` float array."""
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(0)
        if head == b"solid":
            text = f.read().decode("ascii", errors="ignore")
            if "facet" in text:
                return _read_stl_ascii(text)
        return _read_stl_binary(path)


def _read_stl_ascii(text):
    verts = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("vertex"):
            parts = line.split()
            verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
    v = np.asarray(verts, dtype=float)
    return v.reshape(-1, 3, 3)


def _read_stl_binary(path):
    with open(path, "rb") as f:
        f.read(80)                                   # header
        (n,) = struct.unpack("<I", f.read(4))
        tris = np.empty((n, 3, 3), dtype=float)
        for k in range(n):
            data = struct.unpack("<12fH", f.read(50))  # normal + 3 verts + attr
            tris[k, 0] = data[3:6]
            tris[k, 1] = data[6:9]
            tris[k, 2] = data[9:12]
    return tris


# --------------------------------------------------------------------------- #
# JSON scene loader
# --------------------------------------------------------------------------- #
def _vec(j):
    return np.array([float(j[0]), float(j[1]), float(j[2])], dtype=float)


def load_scene(filename):
    """Parse a ``.json`` scene file.

    Returns ``(camera, objects, lights)`` where ``objects`` is a list of
    :class:`Object` and ``lights`` a list of light dataclasses.
    """
    with open(filename) as f:
        j = json.load(f)
    here = os.path.dirname(os.path.abspath(filename))

    # camera ----------------------------------------------------------------- #
    jc = j["camera"]
    v = _vec(jc["up"]); v = v / np.linalg.norm(v)
    w = -_vec(jc["look"]); w = w / np.linalg.norm(w)
    u = np.cross(v, w)
    camera = Camera(
        eye=_vec(jc["eye"]), u=u, v=v, w=w,
        d=float(jc["focal_length"]),
        width=float(jc["width"]), height=float(jc["height"]),
    )

    # materials -------------------------------------------------------------- #
    materials = {}
    for jm in j.get("materials", []):
        materials[jm["name"]] = Material(
            ka=_vec(jm["ka"]), kd=_vec(jm["kd"]),
            ks=_vec(jm["ks"]), km=_vec(jm["km"]),
            phong_exponent=float(jm["phong_exponent"]),
        )

    # lights ----------------------------------------------------------------- #
    lights = []
    for jl in j.get("lights", []):
        if jl["type"] == "directional":
            d = _vec(jl["direction"]); d = d / np.linalg.norm(d)
            lights.append(DirectionalLight(direction=d, I=_vec(jl["color"])))
        elif jl["type"] == "point":
            lights.append(PointLight(position=_vec(jl["position"]), I=_vec(jl["color"])))

    # objects ---------------------------------------------------------------- #
    objects = []
    for jo in j.get("objects", []):
        t = jo["type"]
        if t == "sphere":
            geom = Sphere(center=_vec(jo["center"]), radius=float(jo["radius"]))
        elif t == "plane":
            normal = _vec(jo["normal"]); normal = normal / np.linalg.norm(normal)
            geom = Plane(point=_vec(jo["point"]), normal=normal)
        elif t == "triangle":
            c = jo["corners"]
            geom = Triangle(a=_vec(c[0]), b=_vec(c[1]), c=_vec(c[2]))
        elif t == "soup":
            tris = read_stl(os.path.join(here, jo["stl"]))
            geom = Soup(triangles=tris)
        else:
            raise ValueError(f"unknown object type {t!r}")
        mat = materials.get(jo.get("material"))
        objects.append(Object(geometry=geom, material=mat))

    return camera, objects, lights


# --------------------------------------------------------------------------- #
# Shared deterministic scenes used by the tests and golden generator
# --------------------------------------------------------------------------- #
def first_hit_demo_scene(variant="public"):
    """A tiny sphere + plane + triangle scene for the ``first_hit`` test.

    ``variant="private"`` returns a differently-shaped scene (different sphere
    centre/radius, a tilted plane and a triangle elsewhere) used only by the
    instructor's private grading fixture.
    """
    grey = Material(ka=np.full(3, 0.3), kd=np.full(3, 0.6),
                    ks=np.full(3, 0.2), km=np.zeros(3), phong_exponent=50.0)
    if variant == "private":
        objects = [
            Object(Sphere(center=np.array([0.4, 0.25, -0.6]), radius=0.75), grey),
            Object(Plane(point=np.array([0.0, -1.4, 0.0]),
                         normal=np.array([0.15, 1.0, 0.1])), grey),
            Object(Triangle(a=np.array([-3.5, -1.0, 0.5]),
                            b=np.array([-1.5, -1.2, -0.5]),
                            c=np.array([-2.5, 1.4, 0.0])), grey),
        ]
        return objects
    objects = [
        Object(Sphere(center=np.array([0.0, 0.0, 0.0]), radius=1.0), grey),
        Object(Plane(point=np.array([0.0, -1.0, 0.0]),
                     normal=np.array([0.0, 1.0, 0.0])), grey),
        Object(Triangle(a=np.array([2.0, -1.0, 0.0]),
                        b=np.array([4.0, -1.0, 0.0]),
                        c=np.array([3.0, 1.0, 0.0])), grey),
    ]
    return objects


def soup_demo_scene(variant="public"):
    """A triangle-soup + plane scene for ``first_hit``'s soup dispatch.

    ``variant="private"`` returns a soup with more (and differently placed)
    triangles, used only by the instructor's private grading fixture.
    """
    grey = Material(ka=np.full(3, 0.3), kd=np.full(3, 0.6),
                    ks=np.full(3, 0.2), km=np.zeros(3), phong_exponent=50.0)
    if variant == "private":
        # Tilted out of any axis plane, so the soup normals differ from the
        # public scene's as well as its positions.
        tris = np.array([
            [[-1.2, -0.2, -0.4], [0.8, -0.35, -0.9], [-0.2, 1.3, -0.15]],
            [[-1.0, 0.1, -3.0], [1.0, -0.2, -2.6], [0.0, 1.1, -3.4]],
            [[-2.5, -0.4, -1.2], [-0.9, -0.55, -1.9], [-1.7, 0.9, -1.4]],
        ])
    else:
        tris = np.array([
            [[-1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],      # front
            [[-1.0, 0.0, -2.0], [1.0, 0.0, -2.0], [0.0, 1.0, -2.0]],   # behind it
        ])
    if variant == "private":
        plane = Plane(point=np.array([0.0, -1.15, 0.0]),
                      normal=np.array([-0.2, 1.0, 0.25]))
    else:
        plane = Plane(point=np.array([0.0, -1.0, 0.0]),
                      normal=np.array([0.0, 1.0, 0.0]))
    objects = [
        Object(Soup(triangles=tris), grey),
        Object(plane, grey),
    ]
    return objects


# --------------------------------------------------------------------------- #
# Render loops (driven by the student's graded functions)
# --------------------------------------------------------------------------- #
_COLOR_MAP = np.array([
    [228, 26, 28], [55, 126, 184], [77, 175, 74], [152, 78, 163],
    [255, 127, 0], [255, 255, 51], [166, 86, 40], [247, 129, 191],
    [153, 153, 153],
], dtype=np.uint8)


DEFAULT_IMAGE_HEIGHT = 180


def image_size(camera, width=None, height=None,
               default_height=DEFAULT_IMAGE_HEIGHT):
    """Pixel dimensions to render ``camera`` at, keeping pixels square.

    The scene file describes the image plane in *scene* units, so a camera with
    ``"width": 1, "height": 1`` is asking for a square picture. Rendering that
    into a grid of a different shape stretches everything in it -- a sphere
    comes out as an ellipse. So whichever dimension is not pinned explicitly is
    derived from the camera's own aspect ratio.

    Passing both a width and a height pins them, stretch and all.
    """
    aspect = float(camera.width) / float(camera.height)
    if width is None and height is None:
        height = default_height
    if width is None:
        width = round(height * aspect)
    elif height is None:
        height = round(width / aspect)
    return max(1, int(width)), max(1, int(height))


def render_part1(camera, objects, width, height, viewing_ray, first_hit):
    """Part 1 (ray casting) false-colour buffers: object-id, depth, normal."""
    id_img = np.zeros((height, width, 3), dtype=np.uint8)
    depth_img = np.zeros((height, width), dtype=np.uint8)
    normal_img = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            ray = viewing_ray(camera, i, j, width, height)
            hit, hit_id, t, n = first_hit(ray, 1.0, objects)
            if not hit:
                continue
            cid = hit_id % len(_COLOR_MAP)
            id_img[i, j] = _COLOR_MAP[cid]
            depth = camera.d / (t * np.linalg.norm(ray.direction))
            depth = min(depth, 1.0)
            depth_img[i, j] = np.uint8(255.0 * depth)
            normal_img[i, j] = np.clip(255.0 * (n * 0.5 + 0.5), 0, 255).astype(np.uint8)
    return id_img, depth_img, normal_img


# Names of the shading stages, in the order each term is added. Rendering a
# scene one stage at a time is the fastest way to localise a bug: the first
# image that looks wrong tells you which term to go and read.
STAGES = ("ambient", "diffuse", "specular", "shadows", "reflection")

STAGE_BLURB = {
    "ambient": "0.1 * ka only - a flat silhouette of each object's ambient colour",
    "diffuse": "+ kd * I * max(0, n.l) - shape appears, lit from the light's side",
    "specular": "+ ks * I * max(0, n.h)^p - highlights appear on shiny materials",
    "shadows": "+ occlusion test - objects now cast shadows on each other",
    "reflection": "+ km * reflected colour - mirror surfaces pick up the scene",
}


def _material_without(material, drop):
    """A copy of ``material`` with the named coefficients zeroed."""
    zero = np.zeros(3)
    return Material(
        ka=np.zeros(3) if "ka" in drop else np.asarray(material.ka, dtype=float),
        kd=zero if "kd" in drop else np.asarray(material.kd, dtype=float),
        ks=zero if "ks" in drop else np.asarray(material.ks, dtype=float),
        km=zero if "km" in drop else np.asarray(material.km, dtype=float),
        phong_exponent=material.phong_exponent,
    )


def _objects_without(objects, drop):
    """The scene with the named coefficients zeroed on every material."""
    return [Object(geometry=o.geometry, material=_material_without(o.material, drop))
            for o in objects]


def render_stage(camera, objects, lights, width, height, stage,
                 viewing_ray, first_hit, blinn_phong_shading, raycolor):
    """Render one shading stage as a ``uint8`` ``(H, W, 3)`` image.

    Every stage is produced by *your* functions; the backend only changes what
    it hands them:

    ``ambient``    ``blinn_phong_shading`` with ``kd`` and ``ks`` zeroed
    ``diffuse``    ... with ``ks`` zeroed
    ``specular``   ... with the real material (still no shadows)
    ``shadows``    ... with the whole scene visible to the shadow rays
    ``reflection`` the full ``raycolor``, so mirror bounces are included

    The first four stages suppress shadows by showing the shadow ray only the
    object it started from, so nothing else can occlude it. (A convex object
    cannot shadow its own lit side, so this really is "shadows off".)
    """
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage!r}; expected one of {list(STAGES)}")

    drop = {"ambient": ("kd", "ks", "km"),
            "diffuse": ("ks", "km"),
            "specular": ("km",),
            "shadows": ("km",),
            "reflection": ()}[stage]
    staged = _objects_without(objects, drop)

    out = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            ray = viewing_ray(camera, i, j, width, height)
            if stage == "reflection":
                hit, rgb = raycolor(ray, 1.0, staged, lights, 0)
            else:
                hit, hit_id, t, n = first_hit(ray, 1.0, staged)
                if not hit:
                    continue
                if stage == "shadows":
                    rgb = blinn_phong_shading(ray, hit_id, t, n, staged, lights)
                else:
                    # Hand the shader a one-object scene so its shadow rays
                    # cannot find any occluder.
                    rgb = blinn_phong_shading(ray, 0, t, n, [staged[hit_id]], lights)
            if hit:
                out[i, j] = np.clip(255.0 * np.clip(rgb, 0.0, 1.0), 0, 255).astype(np.uint8)
    return out


def render_part2(camera, objects, lights, width, height, viewing_ray, raycolor):
    """Part 2 (ray tracing) lit RGB image as a ``uint8`` ``(H, W, 3)`` array."""
    out = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            ray = viewing_ray(camera, i, j, width, height)
            hit, rgb = raycolor(ray, 1.0, objects, lights, 0)
            if hit:
                out[i, j] = np.clip(255.0 * np.clip(rgb, 0.0, 1.0), 0, 255).astype(np.uint8)
    return out
