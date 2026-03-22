import cadquery as cq
from ocp_vscode import show

"""
                                    ._.
     _______________________________| |
    /                               | |
    |                               | |
    \_______________________________| |
                                    |_|

"""

total_space_length = 81.5  # mm on stand
washer_size = 1.5  # mm
z_clearance = 0.15
cap_length = 2 - z_clearance
insert_length = 78
assert cap_length + insert_length + washer_size + z_clearance == total_space_length
outer_dia = 15.75
inner_dia = 10.25
cap_dia = 20
tip_chamfer_size = 1
other_chamfer_size = 0.5

result = (
    cq.Workplane("XY")
    .cylinder(insert_length, outer_dia / 2)
    .faces(">Z")
    .edges()
    .chamfer(tip_chamfer_size)
    .faces("<Z")
    .workplane()
    .circle(cap_dia / 2)
    .extrude(cap_length)
    .faces("<Z")
    .workplane()
    .circle(inner_dia / 2)
    .extrude(
        -total_space_length,
        combine="cut",
    )
    .faces(">>Z[1]")
    .edges()
    .chamfer(other_chamfer_size)
)
show(result)
result.export("./dist/cb500x_centre_stand_adapter.step")
