import cadquery as cq
from ocp_vscode import show

width = 50
height = 25
depth = 10
hole1_dia = 16
hole2_dia = 16
pad = 5
max_hole_dia = max(hole1_dia, hole2_dia)
base_fillet = 0.75
squeeze = 1
alignment_pin_dia = 2
alignment_pin_depth = 2
alignment_hole_dia = 2.5
alignment_hole_depth = 2.5
clamp_hole_size = 3.5  # M3
heatsert_diameter = 4.8  # TODO
heatsert_depth = 8.5  # TODO
bolt_head_diameter = 5.5
bolt_head_depth = 3
anti_pinch_radius = 0.4
soft_guide_thickness = 2
# corner_curvature_factor: When making large curves on corners, this is the fillet size as a fraction of the total edge
corner_curvature_factor = 1 / 3
assert 0 < corner_curvature_factor < 1 / 2

vol = (
    cq.Workplane("XY")
    .box(width, height, depth)
    .faces(">Z")
    .workplane()
    .pushPoints([[-width / 2 + pad + max_hole_dia / 2, 0]])
    .hole(hole1_dia)
    .faces(">Z")
    .workplane()
    .pushPoints([[width / 2 - pad - max_hole_dia / 2, 0]])
    .hole(hole2_dia)
)

half_section_height = height / 2 - squeeze / 2
upper_envelope = cq.Workplane("XY").box(width, half_section_height, depth).translate((0, height / 4 + squeeze / 4, 0))
lower_envelope = cq.Workplane("XY").box(width, half_section_height, depth).translate((0, -height / 4 - squeeze / 4, 0))

alignment_pin_locations = [[-width / 2 + pad / 2, 0], [width / 2 - pad / 2, 0]]

upper = (
    vol.intersect(upper_envelope)
    # Curve edges
    .edges("|Z and (not <Y)")
    .fillet(height * corner_curvature_factor)
    # anti pinch chamfer on clamps
    .faces("<Y")
    .edges("(not <X) and (not >X) and |Z")
    .chamfer(anti_pinch_radius)
    # alignment pin
    .faces("<Y")
    .workplane(centerOption="CenterOfBoundBox")
    .pushPoints(alignment_pin_locations)
    .circle(alignment_pin_dia / 2)
    .extrude(alignment_pin_depth)
    # round the tip
    .faces("<Y")
    .edges()
    .fillet(alignment_pin_dia / 4)
    # Bolt hole
    .faces(">Y")
    .workplane()
    .cboreHole(clamp_hole_size, cboreDiameter=bolt_head_diameter, cboreDepth=bolt_head_depth)
    # fillet outer edge
    .faces(
        cq.selectors.StringSyntaxSelector(">X or <X or >Y")
        + cq.selectors.NearestToPointSelector((width / 2, height / 2))
        + cq.selectors.NearestToPointSelector((-width / 2, height / 2)),
    )
    .edges(">Z or <Z")
    .fillet(base_fillet)
)

lower_base = (
    vol.intersect(lower_envelope)
    # anti pinch chamfer on clamps
    .faces(">Y")
    .edges("(not <X) and (not >X) and |Z")
    .chamfer(anti_pinch_radius)
    # alignment pin
    .faces(">Y")
    .workplane(centerOption="CenterOfBoundBox")
    .pushPoints(alignment_pin_locations)
    .hole(alignment_hole_dia, depth=alignment_hole_depth)
    # round base of hole
    .faces("|Y and (not >Y)")
    .edges("%CIRCLE")
    .fillet(alignment_hole_dia / 6)
    # chamfer entry
    .faces(">Y")
    .edges("%CIRCLE and (not >X) and (not <X)")
    .chamfer(alignment_hole_dia / 4)
    # Bolt hole
    .faces("<Y")
    .workplane()
    .cboreHole(clamp_hole_size, cboreDiameter=heatsert_diameter, cboreDepth=heatsert_depth)
)


lower_free = (
    lower_base
    # Curve corners
    .faces("<Y")
    .edges("|Z")
    .fillet(height * corner_curvature_factor)
    # fillet outer edge
    .faces(
        cq.selectors.StringSyntaxSelector(">X or <X or <Y")
        + cq.selectors.NearestToPointSelector((width / 2, -height / 2))
        + cq.selectors.NearestToPointSelector((-width / 2, -height / 2)),
    )
    .edges(">Z or <Z")
    .fillet(base_fillet)
)

tab_thickness = 5
tab_depth = 20
tab_hole_dia = 5
auto_tab_support_chamfer = min(max(0, tab_depth - depth), width / 2 - heatsert_diameter)
tab_support_chamfer = tab_depth - 15

lower_tabbed_90d = (
    lower_base.faces("<Y")
    .workplane(origin=(width / 2 - tab_thickness / 2, 0))
    .rect(tab_thickness, depth)
    .extrude(tab_depth)
    # Curve corner
    .faces("<X")
    .edges("<Y")
    .fillet(height * corner_curvature_factor)
    # curve tab
    .faces("<Y")
    .edges("|X")
    .fillet(depth * corner_curvature_factor)
    # hole in mounting tab
    .faces(">X")
    .workplane(origin=(0, -height / 2 - tab_depth + depth / 2))
    .hole(tab_hole_dia)
    # support for mounting tab
    .faces("-X and (not <X)")
    .edges(">Y")
    .chamfer(tab_support_chamfer)
    # fillet outer edge
    .faces(
        cq.selectors.StringSyntaxSelector(">X or <X or <Y")
        + cq.selectors.NearestToPointSelector((-width / 2, -height / 2))
        + cq.selectors.NearestToPointSelector((width / 4, -height / 2 - tab_support_chamfer)),
    )
    .edges(">Z or <Z")
    .fillet(base_fillet)
)


show(
    upper,
    lower_tabbed_90d.translate((0, -10, 0)),
    lower_free.translate((0, -10, depth * 1.5)),
)

upper.export("./dist/clamp_upper.step")
lower_tabbed_90d.export("./dist/clamp_lower_90d_tab.step")
lower_free.export("./dist/clamp_lower_free.step")
