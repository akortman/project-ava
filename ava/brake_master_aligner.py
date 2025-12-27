import cadquery as cq
from ocp_vscode import show

thickness = 5
existing_hole_spacing = 85, 85
new_hole_spacing = 80, 60

pin_depth = 8
pin_dia = 8.5
hole_dia = 4
base_fillet = 1
drill_guide_chamfer = 1.5
pin_taper_angle = 5

plate_width = max(existing_hole_spacing[0] + pin_dia, new_hole_spacing[0] + hole_dia) + thickness * 2
plate_depth = max(existing_hole_spacing[1] + pin_dia, new_hole_spacing[1] + hole_dia) + thickness * 2

result = (
    cq.Workplane("XY")
    .box(plate_width, plate_depth, thickness)
    .edges("|Z")
    .fillet(max(pin_dia, hole_dia) / 2 + thickness / 2)
    .edges("not |Z")
    .fillet(base_fillet)
    .faces(">Z")
    .workplane()
    .rect(*new_hole_spacing, forConstruction=True)
    .vertices()
    .hole(hole_dia)
    .rect(*existing_hole_spacing, forConstruction=True)
    .vertices()
    .circle(pin_dia / 2)
    .extrude(pin_depth, taper=pin_taper_angle)
    .faces("<Z")
    .edges("%CIRCLE")
    .chamfer(drill_guide_chamfer)
)

show(result)
result.export("./dist/brake_master_aligner.step")
