import cadquery as cq
from ocp_vscode import show

thickness = 8


part_width = 90
part_depth = 45

riser_width = 45
riser_height = 3
riser_depth = part_depth

# Basic box
result = (
    cq.Workplane("XY")
    .box(part_width, part_depth, thickness)
    .faces(">Z")
    .workplane()
    .rect(riser_width, riser_depth)
    .extrude(riser_height)
)

# FPR mount holes
fpr_main_hole_dia = 22
fpr_bolt_spacing = 30
fpr_bolt_hole_dia = 5.5
fpr_bolt_hole_head_depth = 6
fpr_bolt_hole_head_dia = 8.5

# Add some slopes on the side of the riser
result = (
    result.faces("<Y")
    .workplane(origin=(0, 0))
    .moveTo(riser_width / 2, thickness / 2)
    .lineTo(riser_width / 2 + riser_height, thickness / 2)
    .lineTo(riser_width / 2, riser_height + thickness / 2)
    .close()
    .moveTo(-riser_width / 2, thickness / 2)
    .lineTo(-riser_width / 2 - riser_height, thickness / 2)
    .lineTo(-riser_width / 2, riser_height + thickness / 2)
    .close()
    .extrude(-part_depth)
    .combine()
)

# A small cutout to clear the bracket
cutout_depth = 5
cutout_width = part_width - 15 * 2
result = (
    result.faces("<Z")
    .workplane(origin=(0, -part_depth / 2))
    .lineTo(-cutout_width / 2, 0)
    .lineTo(-cutout_width / 2 - cutout_depth, 0)
    .lineTo(-cutout_width / 2, -cutout_depth)
    .lineTo(0, -cutout_depth)
    .lineTo(0 + cutout_depth, 0)
    .close()
    .cutThruAll()
)

# Filleting etc
base_fillet = 1
result = (
    result
    # round corners around bracket holes
    .faces(">Y")
    .edges("|Z")
    .fillet((part_depth - 24) / 2)
    .faces("<Y")
    .edges("|Z and (<X or >X)")
    .fillet(8)
    # round corners
    .edges()
    .fillet(base_fillet)
)

# Add fpr mount
result = (
    result.faces("<Z")
    .workplane(origin=(0, cutout_depth / 2))
    .pushPoints([[0, 0]])
    .hole(fpr_main_hole_dia)
    .pushPoints([[-fpr_bolt_spacing / 2, 0], [fpr_bolt_spacing / 2, 0]])
    .cboreHole(fpr_bolt_hole_dia, cboreDepth=fpr_bolt_hole_head_depth, cboreDiameter=fpr_bolt_hole_head_dia)
    # Add a cutout for the two fpr mount bolts to remove a sharp spot
    .faces("<Z")
    .workplane(origin=(0, cutout_depth / 2))
    .rect(fpr_bolt_spacing, fpr_bolt_hole_head_dia)
    .extrude(-fpr_bolt_hole_head_depth, combine="cut")
)


# Add mounting holes for bracket.
bracket_mount_hole_dia = 8
bracket_hole_positions = [
    [-72 / 2, -13.5],
    [-72 / 2, 13.5],
    [72 / 2, -10.5],
    [72 / 2, 13.5],
]
result = result.faces("<Z").workplane(origin=(0, 0)).pushPoints(bracket_hole_positions).hole(bracket_mount_hole_dia)

bounding_box_width = fpr_bolt_spacing + fpr_bolt_hole_head_dia + 0.5
bounding_box_depth = fpr_main_hole_dia + 0.5

result = (
    result.faces("<Z")
    .edges(
        cq.selectors.BoxSelector(
            (-bounding_box_width / 2, -bounding_box_depth / 2, -100),
            (bounding_box_width / 2, bounding_box_depth / 2, 100),
        ),
    )
    .chamfer(base_fillet)
)
show(result)
result.export("./dist/fpr_mount.step")
result.export("./dist/fpr_mount.stl")
