import cadquery as cq
from ocp_vscode import show
from params import (
    dbw_hole_countersink_dia,
    dbw_hole_dia,
    dbw_lower_left_hole_position,
    dbw_mount_depth,
    dbw_upper_right_hole_position,
    firewall_mount_hole_positions,
    plate_support_radius,
    top_chamfer,
)

additional_support_points = [
    ((dbw_lower_left_hole_position[0] + dbw_upper_right_hole_position[0]) / 2, dbw_upper_right_hole_position[1]),
    ((dbw_lower_left_hole_position[0] + dbw_upper_right_hole_position[0]) / 2, dbw_lower_left_hole_position[1]),
]


def make_support_shape(support_radius: int) -> cq.Sketch:
    shape = cq.Sketch()
    for p in [
        *firewall_mount_hole_positions,
        dbw_lower_left_hole_position,
        dbw_upper_right_hole_position,
        *additional_support_points,
    ]:
        shape = shape.arc(p, support_radius, 0.0, 360.0)
    return shape.hull()


result = cq.Workplane("XY").placeSketch(make_support_shape(plate_support_radius)).extrude(dbw_mount_depth)

# Cut DBW mounting holes
result = (
    result.faces(">Z")
    .workplane()
    .pushPoints(
        [
            dbw_lower_left_hole_position,
            dbw_upper_right_hole_position,
        ],
    )
    .circle(dbw_hole_dia / 2)
    .cutThruAll()
)

# countersink cbw holes
result = (
    result.faces(">Z").edges(cq.selectors.RadiusNthSelector(0)).chamfer((dbw_hole_countersink_dia - dbw_hole_dia) / 2)
)

# countersink counterbore holes
result = result.faces(">Z").edges(cq.selectors.RadiusNthSelector(1)).chamfer(2)

# Curve face edge
result = (
    result.faces(">Z")
    .edges(cq.selectors.InverseSelector(cq.selectors.RadiusNthSelector(0) + cq.selectors.RadiusNthSelector(1)))
    .chamfer(top_chamfer)
)


if __name__ == "__main__":
    show(result)
