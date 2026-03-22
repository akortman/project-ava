"""
Tools to add an SVG as a path to a cadquery workplane.

Original code by:
    Dov Grobgeld <dov.grobgeld@gmail.com>
    2024-03-10 Sun
    https://gist.github.com/dov/8d9b0304ba85e3229aabccac3c6468ef
"""

from math import acos, cos, degrees, fmod, pi, sin, sqrt

import cadquery as cq
import numpy as np
import svgpathtools

type Vec2 = tuple[float, float]


def complex_to_tuple(c: complex) -> Vec2:
    """Convert a complex number to a tuple."""
    return (c.real, c.imag)


def angle_between(u: float, v: float) -> float:
    """Find the angle between the vectors u an v."""
    ux, uy = u
    vx, vy = v
    sign = 1 if ux * vy - uy * vx > 0 else -1
    arg = (ux * vx + uy * vy) / (sqrt(ux * ux + uy * uy) * sqrt(vx * vx + vy * vy))
    return sign * acos(arg)


def arc_endpoint_to_center(  # noqa: PLR0913
    *,
    start: complex,
    end: complex,
    flag_a: bool,
    flag_s: bool,
    radius: float,
    phi: float,
) -> tuple[Vec2, float, float]:
    """
    Convert a endpoint elliptical arc description to a center description.

    Implementation of:
     - https://www.w3.org/TR/SVG/implnote.html#ArcConversionCenterToEndpoint
    """
    rx, ry = radius.real, radius.imag
    x1, y1 = start.real, start.imag
    x2, y2 = end.real, end.imag

    cosphi = cos(phi)
    sinphi = sin(phi)
    rx2 = rx * rx
    ry2 = ry * ry

    # Step 1. Compute x1p,y1p
    x1p, y1p = (np.array([[cosphi, sinphi], [-sinphi, cosphi]]) @ np.array([x1 - x2, y1 - y2]) * 0.5).flatten()
    x1p2 = x1p * x1p
    y1p2 = y1p * y1p

    # Step 2: Compute (cx', cy')
    cxyp = sqrt((rx2 * ry2 - rx2 * y1p2 - ry2 * x1p2) / (rx2 * y1p2 + ry2 * x1p2)) * np.array(
        [rx * y1p / ry, -ry * x1p / rx],
    )

    if flag_a == flag_s:
        cxyp = -cxyp

    cxp, cyp = cxyp.flatten()

    # Step 3: compute (cx,cy) from (cx',cy')
    cx, cy = (cosphi * cxp - sinphi * cyp + 0.5 * (x1 + x2), sinphi * cxp + cosphi * cyp + 0.5 * (y1 + y2))

    # Step 4: compute theta1 and deltatheta
    theta1 = angle_between((1, 0), ((x1p - cxp) / rx, (y1p - cyp) / ry))
    delta_theta = fmod(
        angle_between(((x1p - cxp) / rx, (y1p - cyp) / ry), ((-x1p - cxp) / rx, (-y1p - cyp) / ry)),
        2 * pi,
    )

    # Choose the right edge according to the flags
    if not flag_s and delta_theta > 0:
        delta_theta -= 2 * pi
    elif flag_s and delta_theta < 0:
        delta_theta += 2 * pi

    return (cx, cy), theta1, delta_theta


def add_path_from_svg(workplane: cq.Workplane, path: svgpathtools.Path) -> cq.Workplane:
    """Add the svg path object to the current workspace."""
    path_start = None
    arc_id = 0
    for p in path:
        if path_start is None:
            path_start = p.start
        workplane = workplane.moveTo(*complex_to_tuple(p.start))

        # Support the four svgpathtools different objects
        if isinstance(p, svgpathtools.CubicBezier):
            coords = (
                complex_to_tuple(p.start),
                complex_to_tuple(p.control1),
                complex_to_tuple(p.control2),
                complex_to_tuple(p.end),
            )
            coords = (complex_to_tuple(pt) for pt in (p.start, p.control1, p.control2, p.end))
            workplane = workplane.bezier(coords)
        elif isinstance(p, svgpathtools.QuadraticBezier):
            coords = (complex_to_tuple(pt) for pt in (p.start, p.control, p.end))
            workplane = workplane.bezier(coords)
        elif isinstance(p, svgpathtools.Arc):
            arc_id += 1
            _center, theta1, delta_theta = arc_endpoint_to_center(
                p.start,
                p.end,
                p.large_arc,
                p.sweep,
                p.radius,
                p.rotation,
            )

            workplane = workplane.ellipseArc(
                x_radius=p.radius.real,
                y_radius=p.radius.imag,
                rotation_angle=degrees(p.rotation),
                angle1=degrees(theta1),
                angle2=degrees(theta1 + delta_theta),
            )
        elif isinstance(p, svgpathtools.Line):
            workplane = workplane.lineTo(p.end.real, p.end.imag)

        if path_start == p.end:
            path_start = None
            workplane = workplane.close()

    return workplane


def import_svg(arg: str | svgpathtools.Path, *, workplane: cq.Workplane | None = None) -> cq.Workplane:
    result = workplane or cq.Workplane("XY")

    if isinstance(arg, str):
        paths, _attributes = svgpathtools.svg2paths(arg)
    elif isinstance(arg, svgpathtools.Path):
        paths = [arg]
    else:
        raise TypeError

    if len(paths) == 0:
        raise ValueError("No paths in svg")  # noqa: EM101, TRY003
    if len(paths) > 1:
        print("warning: multiple paths found in svg, using first path")

    return add_path_from_svg(result, paths[0])
