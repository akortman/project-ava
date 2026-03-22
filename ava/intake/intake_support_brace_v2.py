import cadquery as cq
from ocp_vscode import show

support_pillar_size = 25
theta = 60
A = 100
B = 100
diameter = 76
thickness = 8
width = 40
f = 10
h = 76 / 2 + 40

r = diameter / 2


def support_pillar(h: int) -> cq.Workplane:
    return cq.Workplane("XY").circle(support_pillar_size / 2).extrude(h)


pillars = support_pillar(120).union(
    support_pillar(120).translate((B, 0, 0)).rotate((0, 0, 0), (0, 1, 0), -theta).translate((A, 0, 0)),
)

ring = cq.Workplane("XZ").cylinder(width, r + thickness)

result = (
    pillars.union(ring.translate((f, 0, h)))
    .faces("<Y")
    .workplane(centerOption="CenterOfBoundBox")
    .circle(r)
    .cutThruAll()
)

show(result)
