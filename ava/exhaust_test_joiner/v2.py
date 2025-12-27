import cadquery as cq
from ocp_vscode import show

d = 48
thickness = 4
length = 60
bolt_hole_dia = 7
flare_size = 18
squish = 1

inner_radius = d / 2
outer_radius = inner_radius + thickness
entry_chamfer = thickness

cutout_width = d / 1.5
cutout_length = length - 1.5 * flare_size

result = (
    cq.Workplane("XY")
    # arch
    .moveTo(-outer_radius, 0)
    .radiusArc((outer_radius, 0), radius=outer_radius)
    .lineTo(inner_radius, 0)
    .radiusArc((-inner_radius, 0), radius=-inner_radius)
    .close()
    # left flare
    .moveTo(-inner_radius, squish)
    .lineTo(-outer_radius - flare_size, squish)
    .lineTo(-outer_radius - flare_size, thickness + squish)
    .lineTo(-inner_radius, thickness + squish)
    .close()
    # right flare
    .moveTo(inner_radius, squish)
    .lineTo(outer_radius + flare_size, squish)
    .lineTo(outer_radius + flare_size, thickness + squish)
    .lineTo(inner_radius, thickness + squish)
    .close()
    .extrude(length)
    # Cut away `squish` part
    .faces(">Z")
    .workplane(origin=(0, 0))
    .lineTo(outer_radius + flare_size, 0)
    .lineTo(outer_radius + flare_size, squish)
    .lineTo(-outer_radius - flare_size, squish)
    .lineTo(-outer_radius - flare_size, 0)
    .close()
    .extrude(-length, combine="cut")
    # chamfer supports
    .edges("|Z and (not <Y) and (not <X) and (not >X)")
    .chamfer(thickness / 2)
    # chamfer entry
    .edges("|Z and <Y and (not <X) and (not >X)")
    .chamfer(entry_chamfer)
    # cutout center
    .faces("<Y")
    .workplane(origin=(0, 0, length / 2))
    .rect(cutout_width, cutout_length)
    .extrude(-100, combine="cut")
    # fillet corners
    .edges("|Y")
    .fillet(flare_size / 2)
    # fillet edges
    .edges()
    .fillet(1)
    # make bolt holes
    .faces("+Y and %PLANE")
    .workplane(origin=(0, 0))
    .pushPoints(
        [
            (-outer_radius - flare_size / 2, flare_size / 2),
            (-outer_radius - flare_size / 2, length - flare_size / 2),
            (outer_radius + flare_size / 2, flare_size / 2),
            (outer_radius + flare_size / 2, length - flare_size / 2),
            (outer_radius + flare_size / 2, length / 2),
            (-outer_radius - flare_size / 2, length / 2),
        ],
    )
    .hole(bolt_hole_dia)
)

show(result)
result.export("./dist/exhaust_test_joiner.step")
