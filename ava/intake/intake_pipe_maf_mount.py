import cadquery as cq
from ocp_vscode import show


def placeholder(x: float) -> float:
    return x


intake_id = 76
tube_length = 120
wall_thickness = 2
locating_tab_position = 24
locating_tab_depth = 7
locating_tab_width = 3
locating_tab_height = 4  # unimportant
locating_tab_fillet = 0.5
lip_thickness = 1
lip_depth = 2
maf_position = 58
maf_mount_id = 27
maf_mount_standoff_thickness = 4
maf_mount_standoff_height = 2
maf_holes = [
    (placeholder(22.5), placeholder(13)),
    (placeholder(-10), placeholder(-24)),
]
maf_screw_hole_id = 6
maf_screw_hole_depth = 7
maf_screw_mount_od = 10
maf_screw_mount_height = 5.5  # MEASURED FROM `maf_mount_standoff_height` from top radius of pipe
maf_screw_mount_taper = 5

"""
Side profile
---

        |<-----intake_id----->|
         _____________________    __
        (______lip____________)   ^
        |                     |   |   locating_tab_position
        |          _          |  _v__v
        |         | |         |      |    locating_tab_depth
        |         |_|         |     _|_
        |                     |      ^
        |        >| |<        |
        | locating_tab_width  |
        |                     |
        |                     |
        |                     |
        |                     |
        |                     |
        |                     |
        |                     |
        |                     |
        ~~~~~~~~~~~~~~~~~~~~~~~ (unsure) of what to do from here

                            >| |< wall_thickness
    z
    _
    ^
    |
    *---->|xy

Lip dimensions
---

                wall_thickness
    z           |<->|
    _               |
    ^              >|--|< lip_thickness
    |           .___.      ___
    *---->|xy   |   |\      ^
                |   | \     |
                |   |  |    |   lip_depth
                |   |  |    |
                |   | /     |
                |   |/     _v_
                |   |
                |~~~|
             (pipe wall)


MAF mount features
---
             ___________________________________________               ___
            (___________________________________________)               ^
            |                                           |               |
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~              |
            |                     _                     |               |
            |                    | |  (locating tab)    |               |
            |                    |_|                    |         maf_position
            |                                           |               |
            |         maf_holes_0_x                     |               |
            |            |<------>|                     |               |
            |       v    |                              |               |
            |      -*----O       ___                _   |               |
      maf_holes_0_y |          /     \              ^   |               v
            |      -*-        |   .   |   -*-       | maf_mount_id     -*-
            |       ^          \     /     |        v   |
            |                    ---       |        -   |
maf_mount_standoff_thickness >||<            |  maf_holes_1_y
            |                          O---*-           |
            |                     |<-->|                |
            |                       maf_holes_1_x       |
            |                                           |
            |                                           |
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


# base pipe
tube = cq.Workplane("XY").circle(intake_id / 2 + wall_thickness).extrude(tube_length)


# workplane for features
def feature_plane(tube_pos: float = 0, x_offset: float = 0) -> cq.Workplane:
    feature_edge = tube.edges("|Z and >X").val()
    return cq.Workplane(
        cq.Plane(origin=feature_edge.positionAt(0.0) + cq.Vector(x_offset, 0, tube_pos), normal=(1, 0, 0)),
    )


# locating tab
locating_tab_offset = wall_thickness / 2
locating_tab = (
    feature_plane(locating_tab_position + locating_tab_depth / 2, x_offset=-locating_tab_offset)
    .rect(locating_tab_depth, locating_tab_width)
    .extrude(locating_tab_height + locating_tab_offset)
)

# end lip
lip_revolve_r = intake_id / 2 + wall_thickness
lip1 = (
    cq.Workplane("XZ", origin=(lip_revolve_r, 0, lip_depth / 2))
    .ellipse(
        lip_thickness,
        lip_depth / 2,
    )
    .revolve(360, (-lip_revolve_r, 0, 0), (-lip_revolve_r, 1, 0))
)
lip2 = lip1.translate((0, 0, tube_length - lip_depth))

# maf mount ring
maf_mount_offset = intake_id / 2
maf_mount_outer = (
    feature_plane(maf_position, x_offset=-maf_mount_offset)
    .circle(maf_mount_id / 2 + maf_mount_standoff_thickness)
    .extrude(maf_mount_offset + maf_mount_standoff_height)
)

# maf mount screw holes
maf_mount_standoffs = (
    feature_plane(maf_position, x_offset=maf_mount_standoff_height + maf_screw_mount_height)
    .pushPoints(maf_holes)
    .circle(maf_screw_mount_od / 2)
    .extrude(-maf_mount_offset, taper=-maf_screw_mount_taper)
    .pushPoints(maf_holes)
    .circle(maf_screw_hole_id / 2)
    .extrude(-maf_screw_hole_depth, combine="cut")
)

result = (
    tube.union(maf_mount_outer)
    # Cutaway hole for MAF
    .faces(">X")
    .workplane(origin=(0, 0, maf_position))
    .circle(maf_mount_id / 2)
    .extrude(-intake_id / 2, combine="cut")
    # Cut away inner part of tube
    .faces("<Z")
    .workplane(origin=(0, 0, 0), invert=True)
    .circle(intake_id / 2)
    .extrude(tube_length, combine="cut")
    # Select edges for filleting around MAF mount
    # this has some weird geometry and is quite hard to select
    # maf inner mouth & base of outer standoff (these are really hard to separate)
    .edges("(not %CIRCLE) and (not %LINE)")
    .fillet(0.7 * wall_thickness)
    # maf outer mouth & maf standoff outer
    .faces(">X")
    .edges()
    .fillet(maf_mount_standoff_thickness / 3)
)

result = (
    result
    # Add other features
    .union(locating_tab)
    .union(maf_mount_standoffs)
    .union(lip1)
    .union(lip2)
    # Fillet between lip and tube
    .faces(cq.selectors.NearestToPointSelector((-intake_id / 2 - wall_thickness, 0, tube_length / 2)))
    .edges(
        ">Z or <Z",
    )
    .fillet(lip_thickness / 2)
)

result = (
    result
    # Cut away inner part of tube again to remove the standoffs
    .faces("<Z")
    .workplane(origin=(0, 0, 0), invert=True)
    .circle(intake_id / 2)
    .extrude(tube_length, combine="cut")
)
show(result)

result = (
    result
    # tube end inner
    .faces(">Z")
    .edges(cq.selectors.RadiusNthSelector(0))
    .fillet(wall_thickness / 2)
    # tube start inner
    .faces("<Z")
    .edges(cq.selectors.RadiusNthSelector(0))
    .fillet(wall_thickness / 2)
    # maf mount screw #2 standoff, base
    .edges("(not %CIRCLE) and (not %LINE) and (>>Y[-2])")
    .fillet(1)
    # maf mount screw #1 standoff, base
    .edges("(not %CIRCLE) and (not %LINE) and (>>Y[3])")
    .fillet(1)
    # maf mount screw standoff top faces
    .faces(">X")
    .fillet(0.5)
    # locator tab
    .faces("|Z or |Y")
    .edges()
    .fillet(0.5)
)

bounding_box = cq.Workplane("XY", origin=(intake_id * 0.75, 0, tube_length / 2)).box(intake_id, intake_id, intake_id)

show(result)
result.export("./dist/intake_pipe_maf_mount.step")
