"""
Coupler between the MAF and the 60 degree elbow that runs to the filter.

The MAF pipe is slightly thicker (as it's nylon vs the elbow's aluminium), so this needs to be able to step down a
little in size.
"""

import cadquery as cq
from ocp_vscode import show

total_length = 60
adapter_diameter = 88


maf_tube_outer_diameter = 80
maf_tube_insert_depth = 25
inlet_tube_outer_diameter = 76
inlet_tube_insert_length = 20

mid_section_length = total_length - maf_tube_insert_depth - inlet_tube_insert_length
mid_section_diameter = 76


clamp_retainer_depth = 3
clamp_retainer_width = 3

groove_depth = 1.5
groove_width = 3

maf_chamfer_size = (adapter_diameter - maf_tube_outer_diameter + 2 * clamp_retainer_depth) / 4
inlet_chamfer_size = (adapter_diameter - inlet_tube_outer_diameter + 2 * clamp_retainer_depth) / 4

result = (
    cq.Workplane("XY")
    .cylinder(total_length, adapter_diameter / 2)
    # Center retainer=
    .cylinder(clamp_retainer_width * 2, adapter_diameter / 2 + clamp_retainer_depth)
    # Retainer on each side
    .faces(">Z")
    .workplane(invert=True)
    .cylinder(clamp_retainer_width, adapter_diameter / 2 + clamp_retainer_depth)
    .faces("<Z")
    .workplane(invert=True)
    .cylinder(clamp_retainer_width, adapter_diameter / 2 + clamp_retainer_depth)
    # Cut away internals
    .faces("<Z")
    .workplane(invert=True)
    .circle(maf_tube_outer_diameter / 2)
    .cutBlind(maf_tube_insert_depth)
    .faces(">Z")
    .workplane(invert=True)
    .circle(inlet_tube_outer_diameter / 2)
    .cutBlind(maf_tube_insert_depth)
    # Cut inside adapter - this is the smallest diameter so we can just cut through the entire thing
    .faces("<Z")
    .workplane()
    .circle(mid_section_diameter / 2)
    .cutThruAll()
    # grooves for bead
    .faces("<Z[2]")
    .workplane()
    .cylinder(
        groove_width,
        inlet_tube_outer_diameter / 2 + groove_depth,
        combine="cut",
    )
    .faces(">Z[2]")
    .workplane()
    .cylinder(
        groove_width,
        maf_tube_outer_diameter / 2 + groove_depth,
        combine="cut",
    )
    # chamfers for insertion
    .faces("<Z")
    .edges(cq.selectors.RadiusNthSelector(0))
    .chamfer(maf_chamfer_size)
    .faces(">Z")
    .edges(cq.selectors.RadiusNthSelector(0))
    .chamfer(inlet_chamfer_size)
    # Rounding
    .edges()
    .fillet(0.5)
)


show(
    result,
)
result.export(f"./dist/tube_joiner_{maf_tube_outer_diameter}mm_to_{inlet_tube_outer_diameter}mm_dia.step")
