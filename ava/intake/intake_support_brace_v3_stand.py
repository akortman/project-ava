import cadquery as cq
from ocp_vscode import show

diameter = 25
base_chamfer = 2.5

insert_diameter = 5.5
insert_depth = 11
insert_chamfer = 1

for height in [40, 65]:
    result = (
        cq.Workplane("XY")
        .cylinder(height, diameter / 2)
        .faces("<Z or >Z")
        .chamfer(base_chamfer)
        .faces("<Z")
        .workplane()
        .cskHole(insert_diameter, depth=insert_depth, cskDiameter=insert_diameter + insert_chamfer * 2, cskAngle=45)
        .faces(">Z")
        .workplane()
        .cskHole(insert_diameter, depth=insert_depth, cskDiameter=insert_diameter + insert_chamfer * 2, cskAngle=45)
    )

    show(result)
    result.export(f"dist/intake_support_brace_v3_stand_{height}mm.step")
