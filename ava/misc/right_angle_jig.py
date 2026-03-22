import cadquery as cq
from ocp_vscode import show

thickness = 5
height = 25
length1 = 60
length2 = 90
corner_support_distance = 50
corner_support_thickness = thickness
handling_fillet = 1

result = (
    cq.Workplane("XY")
    .box(thickness, length1 + thickness, height)
    .faces(">X")
    .workplane(origin=(0, -length1 / 2, 0))
    .rect(thickness, height)
    .extrude(length2)
    .faces("<Z")
    .workplane(invert=True)
    .polyline([(0, 0), (0, corner_support_distance + thickness / 2), (corner_support_distance + thickness / 2, 0)])
    .close()
    .extrude(corner_support_thickness)
)
show(result)

result = (
    result.edges("<Y and <X and |Z")
    .fillet(thickness)
    .faces(">Z or <Z or <X or <Y or >X or >Y")
    .fillet(handling_fillet)
    .edges(cq.selectors.NearestToPointSelector((length2 / 2, 0, 0)))
    .chamfer(min(thickness / 3, thickness - handling_fillet - 0.1))
)

show(result)
result.export("./dist/right_angle_jig.step")
