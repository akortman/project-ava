import cadquery as cq
from ocp_vscode import show

cqs = cq.selectors

diameter = 77
intake_support_thickness = 10
leg_thickness = 5
mounting_plate_thickness = 5
additional_intake_support_width = 15

mounting_slot_length = 50
mounting_slot_separation = 39
mounting_slot_hole_dia = 12
mounting_slot_hole_clearance = 24
mounting_leg_height = 10

mounting_leg_total_length = mounting_slot_length + mounting_slot_hole_clearance + leg_thickness * 2
mounting_leg_total_width = (
    mounting_slot_separation + mounting_slot_hole_dia + mounting_slot_hole_clearance + leg_thickness * 2
)

intake_support_width = mounting_leg_total_width + additional_intake_support_width

total_height = mounting_leg_height + intake_support_thickness + diameter / 2

insert_dia = 5

base_profile: cq.Workplane = (
    cq.Workplane("XY")
    .sketch()
    .rect(mounting_leg_total_length, mounting_leg_total_width)
    .vertices()
    .fillet(mounting_slot_hole_clearance / 2 + 2 * leg_thickness)
    .finalize()
)

result = (
    base_profile.extrude(total_height)
    .faces(">Y")
    .workplane(invert=True)
    .circle(diameter / 2 + intake_support_thickness)
    .extrude(intake_support_width)
    .faces("<Y")
    .workplane()
    .circle(diameter / 2)
    .cutThruAll()
    .faces("<Y")
    .workplane()
    .pushPoints([(0, -(diameter / 4 + intake_support_thickness / 2))])
    .rect(diameter + intake_support_thickness * 2, diameter / 2 + intake_support_thickness)
    .cutThruAll()
)

blind_slots: cq.Workplane = (
    result.faces("<Z")
    .workplane(centerOption="CenterOfBoundBox")
    .pushPoints(
        [
            (0, -mounting_slot_separation / 2 - additional_intake_support_width / 2),
            (0, mounting_slot_separation / 2 - additional_intake_support_width / 2),
        ],
    )
    .sketch()
    .rect(mounting_slot_length, mounting_slot_hole_dia)
    .vertices()
    .fillet(mounting_slot_hole_dia / 2)
    .finalize()
)

result = blind_slots.cutThruAll()

mounting_slots: cq.Workplane = (
    result.faces(">Z")
    .workplane(offset=-mounting_plate_thickness)
    .pushPoints(
        [
            (0, -mounting_slot_separation / 2 + additional_intake_support_width / 2),
            (0, mounting_slot_separation / 2 + additional_intake_support_width / 2),
        ],
    )
    .sketch()
    .rect(mounting_slot_length + mounting_slot_hole_clearance - mounting_slot_hole_dia, mounting_slot_hole_clearance)
    .vertices()
    .fillet(mounting_slot_hole_clearance / 2)
    .finalize()
)

result = mounting_slots.extrude(-(total_height - mounting_plate_thickness), combine="cut")

# mounting holes
result = (
    result.faces("<Z")
    .workplane(centerOption="CenterOfBoundBox")
    .rect(diameter + intake_support_thickness, intake_support_width - intake_support_thickness)
    .vertices()
    .cskHole(insert_dia, insert_dia + 1.5, 45)
)

show(result)

result = (
    result.faces("<Y or >Y")
    .edges(cq.selectors.RadiusNthSelector(0))
    .chamfer(intake_support_thickness / 3)
    .faces(">Z")
    .edges(cqs.StringSyntaxSelector("|Y") + cqs.RadiusNthSelector(0, directionMax=False))
    .chamfer(leg_thickness)
)

show(result)
result.export("dist/intake_support_brace_v4.step")
