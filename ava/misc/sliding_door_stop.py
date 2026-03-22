import cadquery as cq
from ocp_vscode import show

inner_diameter = 80
thickness = 4
depth = 10


upper = (
    cq.Workplane("XY")
    .moveTo(-inner_diameter / 2, 0)
    .radiusArc((inner_diameter / 2, 0), inner_diameter / 2)
    .offset2D(thickness)
)

show(upper)
