import math

import cadquery as cq
from dbw_mount import result as dbw_mount
from ocp_vscode import show
from params import (
    dbw_mount_depth,
    dbw_mount_face_angle,
    firewall_elongated_hole_size,
    firewall_hole_dia,
    firewall_hole_spacing,
    firewall_mount_counterbore_dia,
    firewall_mount_depth_to_counterbore,
    firewall_mount_hole_positions,
    firewall_standoff_depth,
    firewall_standoff_dia,
    plate_support_radius,
    top_chamfer,
    underside_fillet,
)

firewall_workplane = (
    cq.Workplane("XY")
    .transformed(
        (-dbw_mount_face_angle, 0, 0),
        offset=(
            0,
            0,
            -(firewall_hole_spacing + plate_support_radius) * math.tan(math.radians(dbw_mount_face_angle)),
        ),
    )
    .transformed(offset=(0, 0, -firewall_standoff_depth))
)

# first, we make the standoffs on the firewall axis
standoffs = (
    firewall_workplane.pushPoints([firewall_mount_hole_positions[0]])
    .circle(firewall_standoff_dia / 2)
    .extrude(firewall_standoff_depth + dbw_mount_depth, taper=-dbw_mount_face_angle)
    .pushPoints([firewall_mount_hole_positions[1]])
    .circle(firewall_standoff_dia / 2)
    .extrude(firewall_standoff_depth + dbw_mount_depth / 2, taper=-dbw_mount_face_angle)
)


result = dbw_mount.union(standoffs)
show(result)

# Cut lower firewall hole
result = (
    result.faces("<Z").workplane(origin=firewall_mount_hole_positions[0]).circle(firewall_hole_dia / 2).cutThruAll()
)

# Cut upper firewall hole
# This one is elongated a little
result = (
    result.faces("<Z")
    .workplane(origin=firewall_mount_hole_positions[1])
    .move(-firewall_hole_dia / 2, 0)
    .line(0, firewall_elongated_hole_size / 2 - firewall_hole_dia / 2)
    .tangentArcPoint((firewall_hole_dia, 0))
    .line(0, -firewall_elongated_hole_size + firewall_hole_dia)
    .tangentArcPoint((-firewall_hole_dia, 0))
    .close()
    .cutThruAll()
)

# Cut counterbores for mounting to firewall.
result = (
    result.faces("<Z")
    .workplane(offset=-firewall_mount_depth_to_counterbore)
    .pushPoints(firewall_mount_hole_positions)
    .circle(firewall_mount_counterbore_dia / 2)
    .extrude(-100, combine="cut")
)

show(result)

# tidy top of plate
result = (
    result.faces(">Z[1]").edges(cq.selectors.InverseSelector(cq.selectors.RadiusNthSelector(0))).fillet(top_chamfer)
)

# tidy underside
result = (
    result.faces("<Z[1]")
    .edges(cq.selectors.InverseSelector(cq.selectors.RadiusNthSelector(0)))
    .chamfer(underside_fillet)
)

show(result)
result.export("dist/throttle_pedal_adapter_v3.step")
