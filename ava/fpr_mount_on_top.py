import cadquery as cq
from ocp_vscode import show

thickness = 6.5


part_width = 90
part_depth = 45

# Basic box
result = cq.Workplane("XY").box(part_width, part_depth, thickness)

# FPR mount holes
fpr_main_hole_dia = 22
fpr_bolt_spacing = 30
fpr_bolt_hole_dia = 5.5

result = (
    result.faces(">Z")
    .workplane()
    .pushPoints([[0, 0]])
    .hole(fpr_main_hole_dia)
    .pushPoints([[-fpr_bolt_spacing / 2, 0], [fpr_bolt_spacing / 2, 0]])
    .hole(fpr_bolt_hole_dia)
)

# standoff
standoff_depth = 14
standoff_width = 18
result = result.union(
    result.faces("<Z")
    .workplane(origin=(-part_width / 2 + standoff_width / 2, 0, 0))
    .rect(standoff_width, part_depth)
    .extrude(standoff_depth),
)

# Add mounting holes for bracket.
bracket_mount_hole_dia = 8
bracket_hole_positions = [72, 24]
bracket_hole_positions = [
    [-72 / 2, -10.5],
    [-72 / 2, 13.5],
    [72 / 2, -13.5],
    [72 / 2, 13.5],
]
result = result.faces(">Z").workplane().pushPoints(bracket_hole_positions).hole(bracket_mount_hole_dia)

# Add support


def support(support_size: list[float]) -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .moveTo(0, 0)
        .lineTo(support_size[0], 0)
        .lineTo(0, -support_size[1])
        .close()
        .extrude(support_size[2])
        .translate((-part_width / 2 + standoff_width, support_size[2] / 2, -thickness / 2))
    )


support1_size = [22, standoff_depth, 6]
support2_size = [22, standoff_depth, 6]
result = result.union(
    support(support1_size).translate((0, part_depth / 2 - support1_size[2] / 2, 0)),
).union(
    support(support2_size).translate((0, -part_depth / 2 + support2_size[2] / 2, 0)),
)

# Filleting etc
support_chamfer = standoff_depth / 3
base_fillet = 1
result = (
    result
    # round corners around bracket holes
    .faces("<X or >X")
    .edges("|Z")
    .fillet((part_depth - 24) / 2)
    # chamfer around supports
    .faces("<X[1]")
    .edges("not <Z")
    .chamfer(5)
    # Fillet all edges
    .faces()
    .edges("not %CIRCLE")
    .fillet(base_fillet)
    .faces("<Z[1]")
    .edges(cq.selectors.RadiusNthSelector(0, directionMax=False))
    .chamfer(1)
)

show(result)
result.export("./dist/fpr_mount.step")
result.export("./dist/fpr_mount.stl")
