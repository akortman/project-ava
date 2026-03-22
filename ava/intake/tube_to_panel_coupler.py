r"""
Adapter for the intake pipe to a panel/airbox.

This can be used to mount a tube to a panel it's passing through.

If you have a tube of a known inner diameter, cut a larger hole into a panel, you can use this as a soft coupling.

It's a ring made out of a specific profile that looks a bit like this:

                                     |X| (panel inserts into here)
                                _____   _____
                               /     \ /     \
                              /      | |      \
                             /       | |       \
                            |        | |        |
     ___                ___/.        | |        | (this half is called the "panel section"
    |   | (clamp zone) |    .        |_|        |  as it supports the panel)
    |   |______________|    .                   |
    |                       .                   |
    |_______________________.___________________|
        <-- (intake tube goes here -->

    (this half is for
    a worm gear clamp,
    or "clamp support")


For assembly:
    1. Insert coupler into panel hole (this requires bending the coupler - if you can't do this step, you should use
        softer TPU or reduce infill %),
    2. Add clamp to clamp zone (loose),
    3. Insert tube through hole & position,
    4. Tighten clamp to finish fitment.
"""

import cadquery as cq
from ocp_vscode import show

# -- Parameters --
# ---- Profile parameters ---
# Minimum depth of the whole part profile
base_depth = 3
# Width of the section the clamp is locatied
clamp_zone_width = 10
# Width of the raised support section on each side of the clamp zone.
# (The right one is actually slightly larger to support a chamfer half this size.)
clamp_support_width = 3
# depth/height of the raised support section on each side of the clammp zone (on top of the base depth)
clamp_support_depth = 3
# total width of panel section (including the slot etc)
panel_section_width = 32
# total depth of panel section
# # (including the base_depth, so this minus the slot depth must still be as thick as the base depth)
panel_section_depth = 20
# ---- Dimensions of joined parts (tube & panel) ----
# Diameter of the inner tube.
# (This might need to be slightly smaller or larger than your actual tube depending on your printer, material, infill)
tube_diameter = 76
panel_hole_diameter = 92
panel_thickness = 2


# -- Derived values --
clamp_support_left_width = clamp_support_width
# This is slightly larger to support a chamfer on a third of the size.
clamp_support_right_width = clamp_support_left_width * 1.5
panel_capture_slot_depth = (panel_hole_diameter - tube_diameter) / 2
clamp_section_width = clamp_support_left_width + clamp_zone_width + clamp_support_right_width
total_width = clamp_section_width + panel_section_width
tube_insertion_chamfer = 2
if panel_section_depth == "auto":
    # TODO: this doesn't quite work yet...
    panel_section_depth = panel_capture_slot_depth + base_depth + 2

panel_section_outer_chamfer_x = panel_section_depth / 2
panel_section_outer_chamfer_y = min(
    panel_section_outer_chamfer_x,
    (panel_section_depth - base_depth - clamp_support_depth) / 2,
)
panel_support_side_width = (panel_section_width - panel_thickness) / 2
panel_slot_chamfer = (panel_support_side_width - panel_section_outer_chamfer_x) / 2
clamp_support_outer_fillet = (base_depth + clamp_support_depth - tube_insertion_chamfer) / 3

# -- Check invariants --
assert panel_capture_slot_depth + base_depth <= panel_section_depth
assert panel_support_side_width * 2 + panel_thickness == panel_section_width

profile = (
    cq.Workplane("XY")
    .line(0, base_depth + clamp_support_depth)
    .line(clamp_support_left_width, 0)
    .line(0, -clamp_support_depth)
    .line(clamp_zone_width, 0)
    .line(0, clamp_support_depth)
    .line(clamp_support_right_width, 0)
    .lineTo(clamp_section_width, panel_section_depth)
    .line(panel_section_width / 2 - panel_thickness / 2, 0)
    .line(0, -panel_capture_slot_depth)
    .line(panel_thickness, 0)
    .line(0, panel_capture_slot_depth)
    .line(panel_section_width / 2 - panel_thickness / 2, 0)
    .line(0, -panel_section_depth)
    .lineTo(0, 0)
    .close()
)

show(profile)

result = profile.revolve(axisStart=(0, -tube_diameter / 2, 0), axisEnd=(1, -tube_diameter / 2, 0))

show(result)

# Large-scale chamfers
result = (
    # chamfer for inserting inner tube
    result.faces("<X or >X")
    .edges(cq.selectors.RadiusNthSelector(0))
    .chamfer(tube_insertion_chamfer)
    # chamfer on outside of panel support
    .faces(">X or (<X[3])")
    .edges(cq.selectors.RadiusNthSelector(0, directionMax=False))
    .chamfer(panel_section_outer_chamfer_y, panel_section_outer_chamfer_x)
    # chamfer for panel support slot
    .faces("(<X[1]) or (<X[2])")
    .edges(cq.selectors.RadiusNthSelector(0, directionMax=False))
    .chamfer(panel_slot_chamfer)
    .faces(">X[3]")
    .edges(cq.selectors.RadiusNthSelector(0, directionMax=True))
    .chamfer(clamp_support_right_width / 3)
)
show(result)

# Final rounding
result = (
    result.edges(cq.selectors.RadiusNthSelector(0, directionMax=False))
    .fillet(panel_slot_chamfer / 3)
    .faces(">X or <X")
    .edges()
    .fillet(clamp_support_outer_fillet)
    .faces("(>X[1]) or (>X[2])")
    .edges(cq.selectors.RadiusNthSelector(0, directionMax=False))
    .fillet(clamp_support_outer_fillet)
    .faces("(>X[3])")
    .edges()
    .fillet(
        (
            panel_section_depth
            - panel_section_outer_chamfer_x
            - clamp_support_right_width / 3
            - clamp_support_depth
            - base_depth
        )
        / 3,
    )
)
show(result)
