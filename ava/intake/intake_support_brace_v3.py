import cadquery as cq
from ocp_vscode import show

diameter = 76
thickness = 10
width = 50

# cutaway shape
cutaway_length = width - 2 * thickness
cutaway_width = 7
cutaway_cbore_depth = 3
cutaway_cbore_width = 15
cutaway_angles = [35, -35]

insert_diameter = 5
insert_depth = 6.5
insert_chamfer = 1.5

side_chamfer_size = 2

result = (
    cq.Workplane("XY")
    .rect(thickness, width)
    .revolve(180, (diameter / 2 + thickness / 2, 0, 0), (diameter / 2 + thickness / 2, 1, 0))
    .translate((-diameter / 2 - thickness / 2, 0, 0))
    .faces("<Y or >Y")
    .edges("not |X")
    .chamfer(side_chamfer_size)
)

cutaway_profile_inner: cq.Workplane = (
    cq.Workplane("XY").sketch().rect(cutaway_width, cutaway_length).vertices().fillet(cutaway_width / 2).finalize()
)
cutaway_profile_outer: cq.Workplane = (
    cq.Workplane("XY")
    .sketch()
    .rect(cutaway_cbore_width, cutaway_length + (cutaway_cbore_width - cutaway_width))
    .vertices()
    .fillet(cutaway_cbore_width / 2)
    .finalize()
)
support_profile = cq.Workplane = (
    cq.Workplane("XY")
    .sketch()
    .rect(cutaway_cbore_width + thickness, width)
    .vertices()
    .fillet((cutaway_cbore_width + thickness) / 2)
    .finalize()
)

for a in cutaway_angles:
    result = result.union(
        support_profile.extrude(thickness / 2)
        .translate((0, 0, diameter / 2 + thickness / 2))
        .rotate((0, 0, 0), (0, 1, 0), a),
    )
    result = result.cut(cutaway_profile_inner.extrude(diameter / 2 + thickness).rotate((0, 0, 0), (0, 1, 0), a))
    result = result.cut(
        cutaway_profile_outer.extrude(diameter / 2 + cutaway_cbore_depth).rotate((0, 0, 0), (0, 1, 0), a),
    )


# Mounting holes
result = (
    result.faces("<Z")
    .workplane()
    .rect(diameter + thickness, width - thickness, forConstruction=True)
    .vertices()
    .hole(
        diameter=insert_diameter,
        depth=insert_depth,
    )
    .faces("<Z")
    .edges("%CIRCLE")
    .chamfer(insert_chamfer)
)


show(result)
result.export("dist/intake_support_brace_v3.step")
