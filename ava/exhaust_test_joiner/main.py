import math

import cadquery as cq
from ocp_vscode import show

width = 15
dia = 50
circumference = 2 * math.pi * dia / 2
overlap = circumference * 1 / 4
length = circumference + overlap
thickness = 1
locking_hole_dia = 2.5
locking_hole_spacing = 4
locking_pin_dia = 2
locking_pin_tip_dia = locking_pin_dia + 0.1
locking_pin_height = thickness + 1
spacing = 40

locking_positions = []
pos = locking_hole_spacing / 2
while pos < length / 2:
    locking_positions.append((0, pos))
    pos += locking_hole_spacing

pos = -locking_hole_spacing / 2
while pos > -length / 2 + locking_hole_dia:
    locking_positions.insert(0, (0, pos))
    pos -= locking_hole_spacing

num_pins = 8
gap_size = 1
num_holes = len(locking_positions) - num_pins - gap_size
pin_positions = locking_positions[:num_pins]
hole_positions = locking_positions[-num_holes:]

result = (
    cq.Workplane("XY")
    .box(width, length, thickness)
    .edges("|Z")
    .fillet(width / 3)
    # .edges("not |Z")
    # .fillet(thickness / 3)
    .faces(">Z")
    .workplane()
    .pushPoints(hole_positions)
    .hole(locking_hole_dia)
    .pushPoints(pin_positions)
    .circle(locking_pin_dia / 2)
    .extrude(locking_pin_height)
    .faces(">Z")
    .circle(locking_pin_tip_dia / 2)
    .extrude(0.5)
    .faces("<Z")
    .edges("%CIRCLE")
    .fillet(thickness / 2)
)

result.union(result.translate((spacing, 0, 0)))

show(result)
result.export(f"./dist/snapwraps/snapwrap_{dia}mm.step")
