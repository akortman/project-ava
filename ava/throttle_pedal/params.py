# XY Positions relative to upper of two firewall mount holes
# Z position relative to firewall (positive toward the driver)

# firewall mount
firewall_hole_dia = 6.5
firewall_elongated_hole_size = 10
firewall_hole_spacing = 50
firewall_standoff_depth = 12
firewall_standoff_dia = 24
firewall_mount_counterbore_dia = 15
firewall_mount_depth_to_counterbore = 20

# dbw mount
dbw_mount_position = (0, -20)  # relative to upper standoff
dbw_mount_depth = 12
dbw_lower_left_hole_position = (-45, -0)
dbw_hole_spacing = (56.61, 77.33)
dbw_hole_dia = 4  # TODO: set up for insert
dbw_hole_countersink_dia = 8
dbw_mount_dimensions = (85, 105)  # TODO: should we derive this?
dbw_mount_face_angle = 5
plate_support_radius = max(18, firewall_standoff_dia)

# tidy
underside_fillet = 2
top_chamfer = 2

# derived
firewall_mount_hole_positions = [
    (0, 0),
    (0, -firewall_hole_spacing),
]
dbw_upper_right_hole_position = (
    dbw_lower_left_hole_position[0] + dbw_hole_spacing[0],
    dbw_lower_left_hole_position[1] + dbw_hole_spacing[1],
)
dbw_mount_hole_positions = [dbw_lower_left_hole_position, dbw_upper_right_hole_position]

# invariants
min_thickness = 2
assert firewall_mount_depth_to_counterbore > firewall_standoff_depth + min_thickness
assert firewall_mount_depth_to_counterbore + min_thickness < firewall_standoff_depth + dbw_mount_depth
assert plate_support_radius >= firewall_standoff_dia / 2
