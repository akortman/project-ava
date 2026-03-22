import cadquery as cq
from ocp_vscode import show

inner_diameter = 80
thickness = 12
depth = 12
side_angle = 45
base_size = 48
base_hole_spacing = 28
base_heatsert_dia = 8  # TODO: Select a heatsert
base_heatsert_depth = 10  # TODO: Select a heatsert
side_heatsert_dia = 6  # TODO: Select a heatsert
side_heatsert_depth = 8  # TODO: Select a heatsert
clamping_bolt_hole_dia = 6
clamping_bolt_head_dia = 10
clamping_amount_on_upper = 10
heatsert_chamfer = 1
mount_fillet = 1
outer_fillet_radius = thickness / 2 - 1

r_i = inner_diameter / 2
r_o = inner_diameter / 2 + thickness

upper = (
    cq.Workplane("XY")
    .moveTo(-r_i, 0)
    .radiusArc((r_i, 0), r_i)
    .line(thickness, 0)
    .radiusArc((-r_o, 0), -r_o)
    .close()
    .extrude(depth)
    # Side filleting
    .faces(">Y")
    .edges("not |Z")
    .fillet(outer_fillet_radius)
    # Holes for bolts
    .faces("<Y")
    .workplane(centerOption="CenterOfMass")
    .pushPoints([(-r_i - thickness / 2, 0), (r_i + thickness / 2, 0)])
    .circle(clamping_bolt_hole_dia / 2)
    .cutThruAll()
    # Flatten around holes for bolts
    .faces("<Y")
    .workplane(centerOption="CenterOfMass", offset=-clamping_amount_on_upper)
    .pushPoints([(-r_i - thickness / 2, 0), (r_i + thickness / 2, 0)])
    .circle(clamping_bolt_head_dia / 2)
    .extrude(-r_o, combine="cut")
    # Extend outward
    .faces("<Y")
    .workplane(centerOption="CenterOfMass", offset=-clamping_amount_on_upper)
    .pushPoints(
        [(-r_i - thickness / 2 - clamping_bolt_head_dia / 2, 0), (r_i + thickness / 2 + clamping_bolt_head_dia / 2, 0)],
    )
    .rect(clamping_bolt_head_dia, thickness)
    .extrude(-r_o, combine="cut")
    # small radius on mount surface
    .edges(cq.selectors.RadiusNthSelector(2, directionMax=False))
    .fillet(mount_fillet)
)

inner_sleeve_thickness = 2
inner_sleeve_diameter = 76
inner_sleeve_retainer_size = 4
tol = 0.5
cut_size = 2
inner_sleeve = (
    cq.Workplane("XY")
    .circle(inner_diameter / 2 + inner_sleeve_thickness + inner_sleeve_retainer_size)
    .extrude(inner_sleeve_thickness)
    .faces(">Z")
    .workplane()
    .circle(inner_diameter / 2 + inner_sleeve_thickness)
    .extrude(thickness + tol)
    .faces(">Z")
    .workplane()
    .circle(inner_diameter / 2 + inner_sleeve_thickness + inner_sleeve_retainer_size)
    .extrude(inner_sleeve_thickness)
    .faces(">Z")
    .workplane()
    .circle(inner_diameter / 2)
    .cutThruAll()
    # Chamer inner edges
    .faces("<Z or >Z")
    .edges(cq.selectors.RadiusNthSelector(0))
    .chamfer(inner_sleeve_thickness / 2)
    # Cut edge so it's easy to fit
    .faces(">Z")
    .workplane(origin=(inner_sleeve_diameter / 2 + inner_sleeve_thickness / 2 + inner_sleeve_retainer_size / 2, 0))
    .rect(inner_sleeve_diameter / 4, cut_size)
    .cutThruAll()
)

show(
    inner_sleeve,
)
