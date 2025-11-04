# from ursina import *
# from ursina.prefabs.ursfx import ursfx
# from ursina.prefabs.sky import Sky
# from ursina.shaders import lit_with_shadows_shader # you have to apply this shader to enties for them to receive shadows.
# import ursina.physics
# import math
# from ursina.lights import DirectionalLight
#
# # Import your track creation function
# from test_2_gemino_track import create_simple_track
#
# # Define the Ursina application
# app = Ursina()
#
# # Lock mouse and remove exit button
# app.mouse.locked = True
# window.exit_button.visible = False
#
# # Enable the physics handler immediately after Ursina app starts.
# # This makes sure the physics world updates.
# ursina.physics.physics_handler.active = True
#
# lit_with_shadows_shader.default_input['shadow_blur'] = 0.005
#
# # Define Player Entity (Car)
# ################################################################################################################################################################################################################################################
# class Player(Entity):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         self.visual_model = Entity(
#             parent=self,
#             model='cube',
#             color=color.red,
#             scale=(3.8, 3.4, 7)
#         )
#         self.visual_model.rotation_y = 180
#
#         self.scale = 1
#         self.position = (0, 1.7, 0)
#         self.shader=lit_with_shadows_shader
#
#         # Create a physics RigidBody for this Entity
#         car_physics_shape = ursina.physics.BoxShape(center=(0,0,0), size=self.visual_model.scale)
#         self.rigid_body = ursina.physics.RigidBody(
#             shape=car_physics_shape,
#             entity=self,
#             mass=1000, # Initial mass for the rigid body
#             kinematic=False,
#             friction=0.5,
#             mask=0x1
#         )
#
#         # Apply damping directly to the rigid body's node for more control
#         self.rigid_body.setLinearDamping(0.1)
#         self.rigid_body.setAngularDamping(1.5) # Increased angular damping for slower, more controlled turns
#         self.rigid_body.setAngularFactor(Vec3(0,1,0)) # Restrict rotation to Y-axis for car-like movement
#
#         # Car Physics Variables (These are applied as forces/torques to the rigid_body)
#         self.engine_thrust_force = 30000
#         self.braking_force = 25000
#         self.reverse_thrust_force = 18000
#         self.handbrake_braking_force = 40000
#
#         self.air_resistance_factor = 0.05
#         self.rolling_resistance_force = 120
#
#         # Sideways Tire Friction (CRITICAL for sliding/drifting)
#         self.sideways_grip_factor = 0.8 # Base grip
#         self.sideways_friction_multiplier = 15000 # Increased for more baseline grip, making traction loss more noticeable
#         self.handbrake_friction_loss_factor = 0.08
#         self.drift_recover_rate = 5.0
#         self.normal_sideways_friction_multiplier = self.sideways_friction_multiplier
#
#         # Natural Drift Thresholds
#         self.drift_threshold_speed = 40
#         self.drift_angular_threshold = math.radians(0.5)
#         self.natural_drift_friction_loss_factor = 0.7 # Increased for sharper traction loss at high speed turns
#
#         # Turning Torque (for speed-scaling and drift impact)
#         self.base_turn_torque_strength = 120000 # Significantly increased for way faster turning
#         self.turn_torque_min_speed_factor = 0.4 # More effective turning even at high speeds
#         self.turn_torque_max_speed_factor = 1.0 # Max turn effectiveness at low speed (e.g., 100% of base)
#         self.turn_torque_speed_scaling_max_speed = 100 # Speed at which turn torque transitions
#         self.angular_drag_torque = 3500
#
#         # Gear System Variables
#         self.current_gear = 1
#         self.max_forward_gear = 5
#         self.boost_multiplier = 1.5
#         self.max_reverse_speed = 60
#
#         self.gear_data = {
#             0: {'max_speed_for_gear': self.max_reverse_speed, 'thrust_multiplier': 1.5, 'upshift_speed': 0, 'downshift_speed': 0},
#             1: {'max_speed_for_gear': 60,  'thrust_multiplier': 3.8, 'upshift_speed': 30, 'downshift_speed': 0},
#             2: {'max_speed_for_gear': 100,  'thrust_multiplier': 3.0, 'upshift_speed': 70, 'downshift_speed': 25},
#             3: {'max_speed_for_gear': 150,  'thrust_multiplier': 2.3, 'upshift_speed': 110, 'downshift_speed': 60},
#             4: {'max_speed_for_gear': 220,  'thrust_multiplier': 1.6, 'upshift_speed': 180, 'downshift_speed': 100},
#             5: {'max_speed_for_gear': 300, 'thrust_multiplier': 1.3, 'upshift_speed': 240, 'downshift_speed': 170},
#         }
#
#         # Drift Mode Toggle (P key)
#         self.slippery_drift_mode = False
#         self.drift_mode_grip_factor = 0.05 # Significantly lower grip in drift mode
#         self.drift_boost_turn_factor = 1.8 # Multiplier for turning torque in drift mode
#
#         # Internal State for Friction Calculation
#         self.current_runtime_sideways_friction_multiplier = self.normal_sideways_friction_multiplier
#         self.handbrake_active = False
#
#         # GUI Elements
#         self.speed_text = Text(text='Speed: 0.0', x=-0.8, y=0.40, scale=1.2, color=color.white)
#         self.gear_text = Text(text='Gear: N', x=-0.8, y=0.35, scale=1.2, color=color.white)
#         self.drift_mode_text = Text(text='Drift Mode (P): OFF', x=-0.8, y=0.30, scale=1.2, color=color.white)
#
#         # Camera Setup
#         camera.parent = self
#         camera.position = (0, 6, -36)
#         camera.rotation_x = 5.5
#
#     def update(self):
#         # Get current speed and forward direction
#         current_speed_magnitude = self.rigid_body.getLinearVelocity().length()
#         dot_forward = self.rigid_body.getLinearVelocity().normalized().dot(self.forward) if current_speed_magnitude > 0.1 else 0
#
#         # Automatic Gear Shifting
#         is_moving_forward = dot_forward > 0.1
#         current_max_speed_for_gear = self.gear_data[self.current_gear]['max_speed_for_gear']
#
#         if is_moving_forward and self.current_gear < self.max_forward_gear:
#             if current_speed_magnitude >= self.gear_data[self.current_gear]['upshift_speed']:
#                 self.current_gear += 1
#         elif is_moving_forward and self.current_gear > 1:
#             if current_speed_magnitude < self.gear_data[self.current_gear]['downshift_speed']:
#                 self.current_gear -= 1
#         elif current_speed_magnitude < 1.0: # Car almost stopped
#             if held_keys['s'] and not is_moving_forward:
#                 self.current_gear = 0 # Set to Reverse
#             elif not held_keys['w'] and not held_keys['s'] and not held_keys['space']:
#                 self.current_gear = 1 # Snap to Neutral/First when idle
#                 self.rigid_body.setLinearVelocity(Vec3(0,0,0))
#
#         # Apply Boost Multipliers if Shift is held
#         current_engine_thrust_force = self.engine_thrust_force
#         current_braking_force = self.braking_force
#         current_reverse_thrust_force = self.reverse_thrust_force
#         current_turn_torque_strength = self.base_turn_torque_strength # Start with base torque
#         current_angular_drag_torque = self.angular_drag_torque
#         current_sideways_grip_factor_base = self.sideways_grip_factor
#         current_rolling_resistance_force = self.rolling_resistance_force
#
#         if held_keys["shift"]: # Boost active
#             current_engine_thrust_force *= self.boost_multiplier
#             current_braking_force *= self.boost_multiplier
#             current_reverse_thrust_force *= self.boost_multiplier
#             current_turn_torque_strength *= self.boost_multiplier
#             current_angular_drag_torque *= 0.75
#             current_sideways_grip_factor_base *= 0.75
#             current_max_speed_for_gear *= self.boost_multiplier
#
#         # Handbrake (Spacebar) Logic
#         if held_keys['space']:
#             self.handbrake_active = True
#             self.rigid_body.apply_central_force(-self.rigid_body.getLinearVelocity().normalized() * self.handbrake_braking_force) # Strong braking
#             self.current_runtime_sideways_friction_multiplier = self.normal_sideways_friction_multiplier * self.handbrake_friction_loss_factor # Reduce sideways grip
#             current_rolling_resistance_force *= 0.2
#         else:
#             self.handbrake_active = False
#             # Sideways Grip Recovery after Handbrake Release
#             if self.current_runtime_sideways_friction_multiplier < self.normal_sideways_friction_multiplier:
#                 local_sideways_speed = self.rigid_body.getLinearVelocity().dot(self.right)
#                 recovery_speed_factor = 1.0
#                 if abs(local_sideways_speed) < 5: # Faster recovery if almost no sideways motion
#                     recovery_speed_factor = 3.0
#
#                 self.current_runtime_sideways_friction_multiplier = lerp(
#                     self.current_runtime_sideways_friction_multiplier,
#                     self.normal_sideways_friction_multiplier,
#                     time.dt * self.drift_recover_rate * recovery_speed_factor
#                 )
#                 self.current_runtime_sideways_friction_multiplier = min(self.current_runtime_sideways_friction_multiplier, self.normal_sideways_friction_multiplier)
#
#         # Apply Input Forces (Thrust and Braking)
#         if held_keys['w']: # Accelerate forward
#             speed_ratio_in_gear = min(1, current_speed_magnitude / current_max_speed_for_gear)
#             effective_thrust = current_engine_thrust_force * self.gear_data[self.current_gear]['thrust_multiplier'] * (1 - speed_ratio_in_gear)
#             self.rigid_body.apply_force(self.forward * effective_thrust, Vec3(0,0,0))
#         elif held_keys['s'] and not held_keys['space']: # Brake or Reverse
#             if dot_forward > 0.1: # Moving forward, apply braking force
#                 self.rigid_body.apply_force(-self.forward * current_braking_force, Vec3(0,0,0))
#             else: # Moving backward or stopped, apply reverse thrust
#                 speed_ratio_reverse = min(1, current_speed_magnitude / self.max_reverse_speed)
#                 effective_reverse_thrust = current_reverse_thrust_force * (1 - speed_ratio_reverse)
#                 self.rigid_body.apply_force(-self.forward * effective_reverse_thrust, Vec3(0,0,0))
#
#         # Apply Turning Torque (Speed Scaled)
#         # Interpolate turn factor: more turning at low speed, less but still significant at high speed.
#         turn_speed_factor_normalized = min(1, current_speed_magnitude / self.turn_torque_speed_scaling_max_speed)
#         speed_scaled_turn_factor = lerp(self.turn_torque_max_speed_factor, self.turn_torque_min_speed_factor, turn_speed_factor_normalized)
#
#         # Boost turning when naturally drifting (sideways speed helps turn)
#         local_sideways_speed = self.rigid_body.getLinearVelocity().dot(self.right)
#         drift_assist_factor = 1 + (abs(local_sideways_speed) / current_speed_magnitude) * 1.2 if current_speed_magnitude > 0.1 else 1.0
#
#         # Apply special drift mode turn boost if P key is active
#         if self.slippery_drift_mode:
#             current_turn_torque_strength *= self.drift_boost_turn_factor
#
#         if held_keys['d']: # Turn right
#             self.rigid_body.apply_torque((0, current_turn_torque_strength * drift_assist_factor * speed_scaled_turn_factor, 0))
#         elif held_keys['a']: # Turn left
#             self.rigid_body.apply_torque((0, -current_turn_torque_strength * drift_assist_factor * speed_scaled_turn_factor, 0))
#
#         # Apply angular drag (resists rotation)
#         if abs(self.rigid_body.getAngularVelocity().y) > 0.1:
#             self.rigid_body.apply_torque((0, -self.rigid_body.getAngularVelocity().y * current_angular_drag_torque, 0))
#         else: # Snap to no rotation if very slight to prevent jitter
#             self.rigid_body.setAngularVelocity(Vec3(0,0,0))
#
#         # Apply Friction Forces (only when car is moving)
#         if current_speed_magnitude > 0.05:
#             # Air Resistance
#             air_resistance_force = self.air_resistance_factor * current_speed_magnitude**2
#             self.rigid_body.apply_central_force(-self.rigid_body.getLinearVelocity().normalized() * air_resistance_force)
#
#             # Rolling Resistance
#             self.rigid_body.apply_central_force(-self.rigid_body.getLinearVelocity().normalized() * current_rolling_resistance_force)
#
#             # Sideways Tire Friction (Crucial for slides/drifts)
#             local_sideways_speed = self.rigid_body.getLinearVelocity().dot(self.right)
#             actual_sideways_velocity = self.right * local_sideways_speed
#             current_sideways_grip_factor_dynamic = current_sideways_grip_factor_base
#
#             # Calculate dynamic sideways grip for natural high-speed/sharp-turn drifts
#             if current_speed_magnitude > self.drift_threshold_speed and abs(self.rigid_body.getAngularVelocity().y) > self.drift_angular_threshold:
#                 speed_over_threshold_normalized = min(1.0, (current_speed_magnitude - self.drift_threshold_speed) / self.drift_threshold_speed)
#                 angular_over_threshold_normalized = min(1.0, (abs(self.rigid_body.getAngularVelocity().y) - self.drift_angular_threshold) / math.radians(3))
#                 # Combine speed and angular momentum to determine grip reduction
#                 reduction_amount = (speed_over_threshold_normalized * 0.5 + angular_over_threshold_normalized * 0.5) * self.natural_drift_friction_loss_factor
#                 reduction_amount = min(reduction_amount, current_sideways_grip_factor_dynamic - 0.1) # Prevent grip from going too low
#                 current_sideways_grip_factor_dynamic -= reduction_amount
#                 current_sideways_grip_factor_dynamic = max(0.1, current_sideways_grip_factor_dynamic) # Clamp min grip
#
#             # Override grip for 'P' (slippery) drift mode
#             if self.slippery_drift_mode:
#                 current_sideways_grip_factor_dynamic = self.drift_mode_grip_factor
#                 self.current_runtime_sideways_friction_multiplier = self.normal_sideways_friction_multiplier * self.handbrake_friction_loss_factor * 0.5
#             else: # Restore friction multiplier when drift mode is off, if not handbraking
#                 if self.current_runtime_sideways_friction_multiplier < self.normal_sideways_friction_multiplier and not self.handbrake_active:
#                     self.current_runtime_sideways_friction_multiplier = lerp(
#                         self.current_runtime_sideways_friction_multiplier,
#                         self.normal_sideways_friction_multiplier,
#                         time.dt * self.drift_recover_rate
#                     )
#
#             # Apply the calculated sideways friction force
#             sideways_friction_force_magnitude = abs(local_sideways_speed) * self.current_runtime_sideways_friction_multiplier * (1 - current_sideways_grip_factor_dynamic)
#             sideways_friction_force_magnitude = min(sideways_friction_force_magnitude, self.engine_thrust_force * 3) # Cap friction force
#
#             if abs(local_sideways_speed) > 0.01:
#                 self.rigid_body.apply_central_force(-actual_sideways_velocity.normalized() * sideways_friction_force_magnitude)
#             else: # Snap sideways force to zero if very slow sideways to prevent jitter
#                 if self.rigid_body.getLinearVelocity().dot(self.right) != 0:
#                     self.rigid_body.apply_central_force(-self.right * self.rigid_body.getLinearVelocity().dot(self.right) * (self.rigid_body.getMass() / time.dt))
#
#             # Coasting Friction (when no throttle/brake input)
#             if not held_keys['w'] and not held_keys['s'] and not held_keys['space']:
#                 if abs(current_speed_magnitude) > 0.05:
#                     coast_friction_force = current_rolling_resistance_force * (min(1, current_speed_magnitude / current_max_speed_for_gear)**2) * 5
#                     self.rigid_body.apply_central_force(-self.forward * coast_friction_force)
#                 elif current_speed_magnitude < 0.5: # Come to a complete stop when very slow and idle
#                     self.rigid_body.setLinearVelocity(Vec3(0,0,0))
#         else: # Car is almost stopped, zero out velocity
#             self.rigid_body.setLinearVelocity(Vec3(0,0,0))
#
#         # Max speed clamping
#         current_speed_magnitude_after_forces = self.rigid_body.getLinearVelocity().length()
#         if current_speed_magnitude_after_forces > 0.1:
#             dot_overall_vs_car_forward = self.rigid_body.getLinearVelocity().normalized().dot(self.forward)
#
#             if dot_overall_vs_car_forward > 0: # Moving forward
#                 if current_speed_magnitude_after_forces > current_max_speed_for_gear:
#                     self.rigid_body.setLinearVelocity(self.rigid_body.getLinearVelocity().normalized() * current_max_speed_for_gear)
#             elif dot_overall_vs_car_forward < 0: # Moving backward
#                 max_reverse_speed_effective = self.max_reverse_speed * (self.boost_multiplier if held_keys["shift"] else 1)
#                 if current_speed_magnitude_after_forces > max_reverse_speed_effective:
#                     self.rigid_body.setLinearVelocity(self.rigid_body.getLinearVelocity().normalized() * max_reverse_speed_effective)
#         else: # Stop completely if very slow
#             self.rigid_body.setLinearVelocity(Vec3(0,0,0))
#
#         # Update GUI
#         self.speed_text.text = f'Speed: {current_speed_magnitude_after_forces:.1f} units/s'
#         if self.current_gear == 0:
#             self.gear_text.text = 'Gear: R'
#         elif self.current_gear == 1 and current_speed_magnitude_after_forces < 1.0 and not held_keys['w'] and not held_keys['s'] and not held_keys['space']:
#             self.gear_text.text = 'Gear: N'
#         else:
#             self.gear_text.text = f'Gear: {self.current_gear}'
#         self.drift_mode_text.text = f'Drift Mode: {"ON" if self.slippery_drift_mode else "OFF"}'
#
#     # Input Handling for Drift Mode Toggle
#     def input(self, key):
#         if key == 'p': # Toggle slippery drift mode with 'p' key
#             self.slippery_drift_mode = not self.slippery_drift_mode
#             # When toggling drift mode, update the friction multiplier immediately
#             if self.slippery_drift_mode:
#                 self.current_runtime_sideways_friction_multiplier = self.normal_sideways_friction_multiplier * self.handbrake_friction_loss_factor * 0.5
#             elif not self.handbrake_active: # Only restore if handbrake isn't active
#                 self.current_runtime_sideways_friction_multiplier = self.normal_sideways_friction_multiplier
#             print(f"Slippery Drift Mode: {'ON' if self.slippery_drift_mode else 'OFF'}")
# ################################################################################################################################################################################################################################################
#
#
# # Create a floor Plane Entity
# floor = Entity(
#     model='plane',
#     scale=(5000, 1, 5000),
#     texture='grass_tintable',
#     color=color.hsv(131, 0.82, 0.26),
#     shader=lit_with_shadows_shader
# )
#
# # Create a RigidBody for the floor, using a PlaneShape and setting it as static (mass=0)
# ursina.physics.RigidBody(
#     shape=ursina.physics.PlaneShape(),
#     entity=floor,
#     mass=0, # Mass of 0 makes it static (unmovable)
#     friction=0.5
# )
#
# # Create an instance of the Skybox prefab
# skybox = Sky()
# # Call the function to create your track
# track_entities = create_simple_track()
# # Create an instance of our Player (car)
# player = Player()
#
# ################################### DEBUG ######################################################################################################################################################################################################
# # EditorCamera for development purposes (uncomment to use)
# EditorCamera()
# # You can uncomment the line below to see the physics colliders for debugging:
# # ursina.physics.physics_handler.debug = True #  Uncomment to verify collisions
# ################################### DEBUG ######################################################################################################################################################################################################
#
#
# # Lighting + Shadow Setup
# light = DirectionalLight(shadow_map_resolution=Vec2(1024, 1024)) # 2048
# light.shadows = True
# light.look_at(Vec3(1, -1, 1))
#
# # Double suns for better texture
# sun = Entity(
#     model='sphere',
#     scale=(75, 75, 75),
#     position=(-450, 450, -450),
#     color=color.hsv(61,0.81,0.93),
#     texture='vertical_gradient',
#     unlit=True
# )
#
# sun2 = Entity(
#     model='sphere',
#     scale=(75, 75, 75),
#     position=(-450, 450, -450),
#     color=color.hsv(61,0.81,0.93),
#     texture='vertical_gradient',
#     unlit=True
# )
#
# update_light = Entity(
#     model='sphere',
#     scale=(1000, 750, 1000),
#     color=color.rgba(1, 1, 1, 0),
#
# )
# update_light.parent = player
#
# def update_light_func():
#     # update_light.world_position = player.world_position
#     # print(f"Lighting Updater Position: {update_light.world_position}")
#     # print(f"Player Position: {player.world_position}")
#     light.update_bounds(entity=update_light) # update the shadow area to fit the bounds of target entity, defaulted to scene.
#
# update_light.update = update_light_func
# # Start the Ursina application
# app.run()
