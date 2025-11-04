from ursina import *
import ursina.physics # Import the physics module here too
from ursina.shaders import lit_with_shadows_shader # you have to apply this shader to enties for them to receive shadows.

def create_test_1():
    track_elements = [] # This list will now contain only the wall

    # --- Define Wall Dimensions ---
    wall_width = 300 # How long the wall is along the X-axis
    wall_height = 50 # How tall the wall is
    wall_thickness = 1 # How thick the wall is (along the Z-axis, if facing forward)

    # --- Create a Single Wall for the car to bump into ---
    # Position it in front of the car's starting point (0, 1, 0)
    # The car starts at Z=0. Let's place the wall further down the Z-axis.
    wall_position_z = 20 # 20 units in front of the origin

    the_wall = Entity(
        model='cube',
        texture='brick', # Or any texture you like
        scale=(wall_width, wall_height, wall_thickness),
        position=(0, wall_height / 2, wall_position_z), # Centered on X, half its height on Y, at specific Z
        color=color.dark_gray,
        shader=lit_with_shadows_shader
    )

    # Create a RigidBody for the wall, ensuring its collision shape matches its visual scale
    the_wall_body = ursina.physics.RigidBody(
        shape=ursina.physics.BoxShape(), # Collision box size matches visual scale
        entity=the_wall,
        mass=0, # Mass of 0 makes it static (unmovable)
        friction=0.7 # Friction for collisions with the car
    )
    track_elements.append(the_wall)

    print(f"Created {len(track_elements)} track elements.")
    return track_elements


def create_track_1():
    track_elements = []

    # New Entity
    ####################################################################################################################
    # --- Define Entity dimensions ---
    wall_width = 450 # How long the wall is along the X-axis
    wall_height = 2 # How tall the wall is
    wall_thickness = 1 # How thick the wall is (along the Z-axis, if facing forward)

    # --- Define Entity position ---
    e1_pos_x = 20
    e1_pos_z = 100

    # --- Define Entity rotation ---
    e1_rot_x = 0
    e1_rot_y = 90
    e1_rot_z = 0

    # Create an Entity
    e1 = Entity(
        model='cube',
        texture='brick', # Or any texture you like
        scale=(wall_width, wall_height, wall_thickness),
        position=(e1_pos_x, wall_height / 2, e1_pos_z), # Half its height on Y so its above ground
        rotation = (e1_rot_x, e1_rot_y, e1_rot_z),
        color=color.dark_gray,
        shader=lit_with_shadows_shader
    )

    # Create the RigidBody for the Entity
    e1b = ursina.physics.RigidBody(
        shape=ursina.physics.BoxShape(), # Collision box size matches visual scale
        entity=e1,
        mass=0, # Mass of 0 makes it static (unmovable)
        friction=0.7 # Friction for collisions with the car
    )
    track_elements.append(e1)
    ####################################################################################################################

    # New Entity
    ####################################################################################################################
    # --- Define Entity dimensions ---
    wall_width = 450 # How long the wall is along the X-axis
    wall_height = 2 # How tall the wall is
    wall_thickness = 1 # How thick the wall is (along the Z-axis, if facing forward)

    # --- Define Entity position ---
    e2_pos_x = -20
    e2_pos_z = 100

    # --- Define Entity rotation ---
    e2_rot_x = 0
    e2_rot_y = 90
    e2_rot_z = 0

    # Create an Entity
    e2 = Entity(
        model='cube',
        texture='brick', # Or any texture you like
        scale=(wall_width, wall_height, wall_thickness),
        position=(e2_pos_x, wall_height / 2, e2_pos_z), # Half its height on Y so its above ground
        rotation = (e2_rot_x, e2_rot_y, e2_rot_z),
        color=color.dark_gray,
        shader=lit_with_shadows_shader
    )

    # Create the RigidBody for the Entity
    e2b = ursina.physics.RigidBody(
        shape=ursina.physics.BoxShape(), # Collision box size matches visual scale
        entity=e2,
        mass=0, # Mass of 0 makes it static (unmovable)
        friction=0.7 # Friction for collisions with the car
    )

    track_elements.append(e2)
    ####################################################################################################################

    # New Entity
    ####################################################################################################################
    # --- Define Entity dimensions ---
    wall_width = 50 # How long the wall is along the X-axis
    wall_height = 2 # How tall the wall is
    wall_thickness = 1 # How thick the wall is (along the Z-axis, if facing forward)

    # --- Define Entity position ---
    e3_pos_x = 10.5
    e3_pos_z = 343.75

    # --- Define Entity rotation ---
    e3_rot_x = 0
    e3_rot_y = 67.5
    e3_rot_z = 0

    # Create an Entity
    e3 = Entity(
        model='cube',
        texture='brick', # Or any texture you like
        scale=(wall_width, wall_height, wall_thickness),
        position=(e3_pos_x, wall_height / 2, e3_pos_z), # Half its height on Y so its above ground
        rotation = (e3_rot_x, e3_rot_y, e3_rot_z),
        color=color.dark_gray,
        shader=lit_with_shadows_shader
    )

    # Create the RigidBody for the Entity
    e3b = ursina.physics.RigidBody(
        shape=ursina.physics.BoxShape(), # Collision box size matches visual scale
        entity=e3,
        mass=0, # Mass of 0 makes it static (unmovable)
        friction=0.7 # Friction for collisions with the car
    )

    track_elements.append(e3)
    ####################################################################################################################


    print(f"Created {len(track_elements)} track elements.")
    return track_elements
