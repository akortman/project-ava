"""
Replica rubber bushing for upper radiator supports on an ST185 GT-Four.

Toyota's design involves two pieces of metal, an upper and lower "cup", that are separated by a bonded piece of rubber
with a big void in the middle.

This design *requires* the upper metal cup part. It does not need the lower part.
"""

import cadquery as cq
from ocp_vscode import show

"""
Basic shape is a cup shape like this:

                             w_outer
            |<------------------------------------->|
        _   ._______________________________________.  _
        ^   |                                 ^     |  ^
        |   |                             t_z |     |  |
        |   |       .______________________.  v     |  |
        |   |       |   ^                ^ |        |  | h_right
 h_left*|   |       |   |   h_inner_right| |        |  |
        |   |       |   |                | |        |  |
        |   |       |   |                v |________|  v.   _
        |   |       |   |h_inner                            ^
        v   |_______|   v                                   | h_right_rise
                                                            v
            |<----->|<-------------------->|<------>|
              t_left       w_inner                t_right

The shape is then filleted and chamfered appropriately.

outer_left_upper_chamfer_z
       |<--->|
     _ .      .______________________________.  .
     ^       /                               \_ outer_right_upper_radius
     |      /                                  \
     |     /     .     _____________   .        \     (<--- inner_left__upper_radius & inner_right_upper_radius)
     |    /         __/             \_          |
     v  ./        _/                  \         |
        |        /                     |        |
        |       /                      \________|
        |       |           inner_right_lower_radius
        |_______/
            inner_left_lower_radius
"""

eps = 0.001
inf = 1000


def approx_eq(a: float, b: float) -> bool:
    return abs(a - b) < eps


# Basic profile parameters.
w_outer = 54
w_inner = 32
t_left = 8
t_right = 14
h_inner = 14
h_inner_right = 12
t_z = 7
h_right = h_inner_right + t_z  # inferred
h_left = h_inner + t_z  # inferred
h_right_rise = h_left - h_right

# 2d-to-3d conversion parameters.
t_x = 32  # Thickness in x-direction

# Post-profile shaping params.
outer_right_upper_radius = 12
outer_left_upper_chamfer_y = 7
outer_left_upper_chamfer_z = 1.8 * outer_left_upper_chamfer_y
outer_left_upper_chamfer_top_radius = 10
outer_left_upper_chamfer_lower_radius = 4
inner_right_upper_radius = 3
inner_left_upper_radius = 16
base_fillet_radius = 1.5
inner_arch_yz_fillet_radius = base_fillet_radius
inner_left_lower_radius = base_fillet_radius
inner_right_lower_radius = inner_left_lower_radius

# Locating pin
locating_pin_location = (
    t_x / 2,
    w_outer - 29,
    0,
)
locating_pin_diameter = 5
locating_pin_height = 5
locating_pin_tip_size = 0.5

# Check invariants.
assert approx_eq(h_inner, (h_left - t_z))
assert approx_eq(h_inner_right, h_right - t_z)
assert approx_eq(w_outer, t_left + w_inner + t_right)
assert h_right < h_left


def make_base() -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .lineTo(0, h_left)
        .lineTo(w_outer, h_left)
        .lineTo(w_outer, h_left - h_right)
        .lineTo(w_outer - t_right, h_left - h_right)
        .lineTo(w_outer - t_right, h_inner)
        .lineTo(t_left + inner_left_upper_radius, h_inner)
        .radiusArc((t_left, 0), radius=-inner_left_upper_radius)
        .close()
        .extrude(t_x)
    )


base = make_base()

result = (
    base
    # Add curve to the outer right side to fit the metal cap.
    .edges(">Z and >Y")
    .fillet(outer_right_upper_radius)
    # Chamfer on the left side
    # This isn't strictly a chamfer but we will use some filleting as well to approximate the geometry.
    .edges(">Z and <Y")
    .chamfer(outer_left_upper_chamfer_y, outer_left_upper_chamfer_z)
    # Fillet the upper edge of the chamfer
    .faces(">Z")
    .edges("<Y")
    .fillet(outer_left_upper_chamfer_top_radius)
    # Fillet the lower edge of the chamfer
    .faces("<Y")
    .edges(">Z")
    .fillet(outer_left_upper_chamfer_lower_radius)
    # Fillet the inner upper right curve to fit the radiator.
    .faces(">Y[-2]")
    .edges(">Z")
    .fillet(inner_right_upper_radius)
    .faces("<Z")
    .edges(">Y")
    .fillet(inner_left_lower_radius)
    .faces("<Z[2]")
    .edges("<Y")
    .fillet(inner_right_lower_radius)
    .faces("<Z")
    .edges("<Y")
    .fillet(base_fillet_radius)
    .faces("<Z[2]")
    .edges(">Y")
    .fillet(inner_right_lower_radius)
    .faces("|X")
    .edges()
    .fillet(base_fillet_radius)
)

locating_pin = (
    result.faces(">Z")
    .workplane(origin=locating_pin_location)
    .cylinder(height=locating_pin_height, radius=locating_pin_diameter / 2)
    .faces(">Z")
    .workplane()
    .cylinder(height=locating_pin_tip_size, radius=locating_pin_diameter / 2 + locating_pin_tip_size)
)

result = result.union(locating_pin)


show(
    result,
    colors=[
        "#59594A",
        "#BE6E46",
    ],
)
result.export("./dist/upper_radiator_bushing.step")
result.export("./dist/upper_radiator_bushing.stl")
