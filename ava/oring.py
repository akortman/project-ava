import cadquery as cq
from ocp_vscode import show

result = cq.Workplane(origin=(20, 0, 0)).circle(2).revolve(180, (-20, 0, 0), (-20, -1, 0))
result2 = cq.Workplane("XZ", origin=(20, 0, 0)).circle(2).revolve(180, (-20, 0, 0), (-20, -1, 0))
show(result2)
