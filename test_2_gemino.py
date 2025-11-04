from ursina import *
from ursina.prefabs.ursfx import ursfx
from ursina.prefabs.sky import Sky
from ursina.lights import DirectionalLight
from ursina.shaders import lit_with_shadows_shader
import ursina.physics
import math


# ---------------- IMPORTS ----------------
# Import Player
from player_entity_class import Player
# Import your track creation function (ensure this file is in the same directory or accessible)
from test_2_gemino_track import create_track_1


# ---------------- APP SETUP ----------------
# Define the Ursina application
app = Ursina()

# Vsync OFF! for smoother physics and higher framerates, though it might cause screen tearing
window.vsync = False

# Lock mouse to the window
app.mouse.locked = True

# Remove the default exit button
window.exit_button.visible = False

# Enable the physics handler immediately after Ursina app starts to ensure physics simulations run.
ursina.physics.physics_handler.active = True

# Adjust shadow blur for the lit_with_shadows_shader to control shadow softness
lit_with_shadows_shader.default_input['shadow_blur'] = 0.005

# ---------------- DEBUGGING TOOLS ----------------
## EditorCamera for development purposes
# EditorCamera()
## See the physics colliders for debugging
# ursina.physics.physics_handler.debug = True
# ---------------- END DEBUGGING TOOLS ----------------


# ---------------- SCENE SETUP ----------------
floor = Entity(
    model='plane',
    scale=(5000, 1, 5000), # Large floor
    texture='grass_tintable',
    texture_scale=(128, 128),
    color=color.hsv(131, 0.82, 0.26), # Greenish grass color
    shader=lit_with_shadows_shader # Apply shader for lighting and shadows
)

# Physics body for the floor (static, immovable)
ursina.physics.RigidBody(
    shape=ursina.physics.PlaneShape(),
    entity=floor,
    mass=0, # Mass 0 makes it static
    friction=0.5 # Friction for the floor
)

# --- Helper Function to Create a Sun Entity Visual ---
def create_sun_visual(initial_position=(-450, 450, -450)):
    """
    Creates and returns an Entity representing a sun visual./
    This function encapsulates all the common properties of your sun.
    """
    return Entity(
        model='sphere',
        scale=(75, 75, 75),
        position=initial_position,
        texture='vertical_gradient',
        # Alpha (a) component of the color for desired opacity.
        color=color.hsv(61,0.81,0.93, a=0.75),
        unlit=True # Not affected by other lights
    )

# Create Sun Visuals using the helper function
# 2 suns for double texture
sun1 = create_sun_visual(initial_position=(-450, 450, -450))
# Adding a slight offset to the second sun to prevent Z-fighting
sun2 = create_sun_visual(initial_position=(-450, 450, -450) + (0.1, 0.1, 0.1))

skybox = Sky() # Environmental skybox

# Create the track using the imported function
track_1 = create_track_1()

# Instantiate the player car
player = Player()


# ---------------- LIGHTING SETUP ----------------
light = DirectionalLight(shadow_map_resolution=Vec2(1024, 1024)) # Directional light for shadows
light.shadows = True # Enable shadows
light.look_at(Vec3(1, -1, 1)) # Set light direction

# Entity to dynamically update light bounds for optimized shadows
update_light = Entity(
    model='sphere', # Invisible model for position reference
    scale=(1000, 750, 1000), # Large scale for shadow area
    color=color.rgba(1, 1, 1, 0), # Fully transparent
)
update_light.parent = player # Parent to player for dynamic bounds

# Function to update the shadow map bounds
def update_light_func():
    light.update_bounds(entity=update_light)

update_light.update = update_light_func # Assign the update function

# ---------------- DEBUGGING TOOLS ----------------
## See Entity wireframes
# for i in scene.entities:
#     i.wireframe = True
# ---------------- END DEBUGGING TOOLS ----------------

# ---------------- APP RUN ----------------
app.run() # Start the Ursina application
