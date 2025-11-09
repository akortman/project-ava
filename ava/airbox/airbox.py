import copy

import cadquery as cq
from ocp_vscode import show

base_length = 250  # TODO
base_width = 160
base_corner_radius = 16
thickness = 2.5
air_filter_retaining_size = 9
side_height = 12
locator_tab_side_lower_offset = 7
locator_tab_side_upper_offset = 5
locator_tab_width = 23.5
locator_tab_x_position = (128 - locator_tab_width) / 2  # Outer edges of locators are 128 apart.

air_pipe_id = 75
air_pipe_od = 80


def rounded_cuboid(x: float, y: float, z: float, r: float) -> cq.Workplane:
    return cq.Workplane("XY").rect(x, y).extrude(z).edges("|Z").fillet(r)


outer_overhanging_shape = (
    rounded_cuboid(base_width, base_length, side_height + thickness, base_corner_radius).faces("|Z").shell(thickness)
)
inner_retaining_shape = (
    rounded_cuboid(base_width, base_length, thickness, base_corner_radius).faces("|Z").shell(-air_filter_retaining_size)
)

# Shape of the "cap" that sits over the air filter.
air_filter_cap = outer_overhanging_shape.union(inner_retaining_shape)

# TODO: locking features
# Tabs extend 7mm below Z-extent of face
# and 5.5mm above Z-extent of face
locator_tab_xy = (
    copy.deepcopy(air_filter_cap)
    .faces(">Y")
    .workplane(centerOption="CenterOfBoundBox")
    .rect(
        side_height + locator_tab_side_lower_offset + locator_tab_side_upper_offset,
        locator_tab_width,
    )
    .extrude(-thickness, combine=False)
    .translate((locator_tab_x_position, 0, (locator_tab_side_lower_offset - locator_tab_side_upper_offset) / 2))
)
locator_tab_xz = locator_tab_xy.mirror(mirrorPlane="XZ")

locator_tabs = (
    locator_tab_xy.union(locator_tab_xy.mirror(mirrorPlane="YZ"))
    .union(locator_tab_xz)
    .union(
        locator_tab_xz.mirror(mirrorPlane="YZ"),
    )
)
# TODO: position air filter pipe outlet

# TODO: loft from filter to outlet

show(
    air_filter_cap,
    locator_tabs,
    colors=["#AAAAAA", "#FF0000"],
    alphas=[1.0, 0.5],
)

air_filter_cap.export("./airbox-filter-cap.step")
