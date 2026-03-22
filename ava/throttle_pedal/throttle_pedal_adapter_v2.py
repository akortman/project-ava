import cadquery as cq
from ocp_vscode import show

# XY Positions relative to upper of two firewall mount holes
# Z position relative to firewall (positive toward the driver)

# firewall mount
firewall_hole_dia = 6.5
firewall_elongated_hole_size = 10
firewall_hole_spacing = 50
firewall_standoff_depth = 12
firewall_standoff_dia = 12
firewall_mount_counterbore_dia = 15
firewall_mount_depth_to_counterbore = 20

# dbw mount
dbw_mount_position = (0, -20)  # relative to upper standoff
dbw_mount_depth = 12
dbw_lower_left_hole_position = (-45, -0)
dbw_hole_spacing = (56.61, 77.33)
dbw_hole_dia = 6  # TODO: set up for insert
dbw_hole_countersink_dia = 8
dbw_mount_dimensions = (85, 105)  # TODO: should we derive this?
plate_support_radius = max(12, firewall_standoff_dia)

# tidy
corner_chamfer = 8
underside_fillet = 1
top_chamfer = 2

# derived
firewall_mount_hole_positions = [
    (0, 0),
    (0, -firewall_hole_spacing),
]
dbw_upper_right_hole_position = (
    dbw_lower_left_hole_position[0] + dbw_hole_spacing[0],
    dbw_lower_left_hole_position[1] + dbw_hole_spacing[1],
)
dbw_mount_hole_positions = [dbw_lower_left_hole_position, dbw_upper_right_hole_position]
total_depth = firewall_standoff_depth + dbw_mount_depth

# invariants
min_thickness = 2
assert firewall_mount_depth_to_counterbore > firewall_standoff_depth + min_thickness
assert firewall_mount_depth_to_counterbore + min_thickness < total_depth

# visualisation of holes for tweaking
hole_positions = (
    cq.Workplane("XY")
    .pushPoints(firewall_mount_hole_positions)
    .circle(firewall_standoff_dia / 2)
    .circle(firewall_hole_dia / 2)
    .extrude(1)
    .pushPoints(dbw_mount_hole_positions)
    .circle(dbw_hole_dia / 2)
    .extrude(1)
)

show(hole_positions)


def make_support_shape(support_radius: int) -> cq.Sketch:
    shape = cq.Sketch()
    for p in [*firewall_mount_hole_positions, dbw_lower_left_hole_position, dbw_upper_right_hole_position]:
        shape = shape.arc(p, support_radius, 0.0, 360.0)
    return shape.hull()


# Base shape.
result = (
    cq.Workplane("XY")
    .pushPoints(firewall_mount_hole_positions)
    .circle(firewall_standoff_dia)
    .extrude(firewall_standoff_depth)
    .faces(">Z")
    .workplane()
    .placeSketch(make_support_shape(plate_support_radius))
    .extrude(dbw_mount_depth)
)

show(result)

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

# Cut counterbores for firewall holes
result = (
    result.faces("<Z")
    .workplane(offset=-firewall_mount_depth_to_counterbore)
    .pushPoints(firewall_mount_hole_positions)
    .circle(firewall_mount_counterbore_dia / 2)
    .extrude(-total_depth, combine="cut")
)

show(result)

# Tidy up:

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

show(
    result,
)
result.export("dist/throttle_pedal_adapter.step")
