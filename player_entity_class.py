from ursina import *
import ursina.physics
from ursina.shaders import lit_with_shadows_shader

# ---------------- PLAYER CLASS ----------------
class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Car's visual model (a simple cube)
        self.visual_model = Entity(
            parent=self,
            model='cube',
            color=color.red,
            scale=(3.8, 3.4, 7) # Dimensions of the car visual
        )
        self.visual_model.rotation_y = 180 # Orient the visual model correctly
        self.scale = 1 # Overall scale of the player entity
        self.position = (0, 1.7, 0) # Initial position of the car
        self.shader=lit_with_shadows_shader # Apply shader for lighting and shadows

        # --- RigidBody Physics Setup ---
        # Define the collision shape for the car's physics body
        car_physics_shape = ursina.physics.BoxShape(center=(0,0,0), size=(3.8, 3.4, 7.0))
        self.rigid_body = ursina.physics.RigidBody(
            shape=car_physics_shape,
            entity=self, # Link the RigidBody to this Ursina Entity
            mass=1000, # Mass in kilograms
            kinematic=False, # Not kinematic, affected by forces and collisions
            friction=0.5, # Bullet's base friction, less relevant than custom sideways friction
            mask=0x1 # Collision mask
        )

        # Set damping for linear and angular velocity
        self.rigid_body.setLinearDamping(0.2) # Faster linear deceleration
        self.rigid_body.setAngularDamping(0.0) # Manual angular damping
        self.rigid_body.setAngularFactor(Vec3(0,1,0)) # Restrict rotation to Y-axis (yaw)

        # --- Car Physics Variables ---
        # Thrust and Braking Forces
        self.engine_thrust_force = 30000 # Base forward acceleration force
        self.braking_force = 25000 # Regular braking force
        self.reverse_thrust_force = 18000 # Reverse thrust force
        self.handbrake_braking_force = 40000 # Strong handbrake force

        # Resistive Forces
        self.air_resistance_factor = 0.05 # Air drag scaling with speed squared
        self.rolling_resistance_force = 120 # Constant rolling resistance

        # --- REVISED DRIFTY PHYSICS SETTINGS ---
        # Sideways Tire Friction (for sliding/drifting)
        self.base_grip_factor = 0.2 # Default grip (0.0 no grip, 1.0 full grip)
        self.handbrake_friction_loss_factor = 0.01 # Handbrake slipperiness
        self.drift_recover_rate = 5.0 # Sideways grip recovery rate
        self.sideways_friction_multiplier = 1500 # MODIFIED: Overall sideways friction multiplier (lower for less speed loss)

        self.current_sideways_grip = self.base_grip_factor # Current grip state

        # Angular Damping (Resists spinning)
        self.base_angular_drag_torque = 12000 # MODIFIED: Increased for faster recentering
        self.angular_drag_speed_scaling_factor = 0.05 # Scales angular drag with speed
        # --- END REVISED DRIFTY PHYSICS ---

        # Natural Drift Thresholds
        self.drift_threshold_speed = 40 # Speed to consider natural drift
        self.drift_angular_threshold = math.radians(0.5) # Angular velocity to trigger natural drift
        self.natural_drift_friction_loss_factor = 0.6 # Grip loss during natural drift

        # Turning Torque
        self.base_turn_torque_strength = 120000 # MODIFIED: Increased for powerful turns
        self.turn_torque_min_speed_factor = 0.7 # MODIFIED: More turning power at high speeds
        self.turn_torque_max_speed_factor = 1.0 # Sharp turns at low speeds
        self.turn_torque_speed_scaling_max_speed = 150 # Speed where turning power scales

        # --- Turning Input Control ---
        self.max_steering_angle_input = 1.0 # Max steering input value
        self.steering_speed = 1.5 # Steering input ramp-up speed
        self.steering_return_speed = 10.0 # MODIFIED: Faster steering input return
        self.current_steering_input = 0.0 # Current smoothed steering input

        # Non-linear steering power
        self.steering_non_linear_power = 1.2 # Nuanced steering feel (small turns slower)
        # --- END ADJUSTED ---

        # --- ANGULAR VELOCITY CAP ---
        self.max_angular_velocity_y = math.radians(200) # Max spin speed
        self.angular_velocity_cap_force = 250000 # Force to counteract excessive spin
        # --- END ANGULAR VELOCITY CAP ---

        # ---------------- GEAR SYSTEM ----------------
        self.current_gear = 1 # Start in 1st gear
        self.max_forward_gear = 5 # Max forward gear
        self.boost_multiplier = 1.5 # Multiplier for boost mode (Shift key)
        self.max_reverse_speed = 60 # Max speed in reverse

        # Gear data: max speed, thrust multiplier, up/downshift points
        self.gear_data = {
            0: {'max_speed_for_gear': self.max_reverse_speed, 'thrust_multiplier': 1.5, 'upshift_speed': 0, 'downshift_speed': 0},
            1: {'max_speed_for_gear': 60,  'thrust_multiplier': 3.8, 'upshift_speed': 30, 'downshift_speed': 0},
            2: {'max_speed_for_gear': 100,  'thrust_multiplier': 3.0, 'upshift_speed': 70, 'downshift_speed': 25},
            3: {'max_speed_for_gear': 150,  'thrust_multiplier': 2.3, 'upshift_speed': 110, 'downshift_speed': 60},
            4: {'max_speed_for_gear': 280,  'thrust_multiplier': 1.6, 'upshift_speed': 180, 'downshift_speed': 100},
            5: {'max_speed_for_gear': 380, 'thrust_multiplier': 1.3, 'upshift_speed': 240, 'downshift_speed': 170},
        }

        # --- EXTREME DRIFT MODE SETTINGS ---
        self.is_extreme_drift_mode = False # Default to OFF
        self.extreme_drift_grip_factor = 0.005 # More reduced grip for extreme drift
        self.extreme_drift_turn_boost = 1.4 # More turn exaggeration in extreme drift
        self.extreme_drift_angular_drag_reduction = 0.2 # Less angular drag in extreme drift
        # --- END EXTREME DRIFT MODE ---

        self.handbrake_active = False # Handbrake state flag

        # ---------------- GUI ELEMENTS ----------------
        self.speed_text = Text(text='Speed: 0.0', x=-0.8, y=0.40, scale=1.2, color=color.white)
        self.gear_text = Text(text='Gear: N', x=-0.8, y=0.35, scale=1.2, color=color.white)
        self.drift_mode_text = Text(text='Extreme Drift Mode : OFF', x=-0.8, y=0.30, scale=1.2, color=color.white)
        self.controls_text_1 = Text(text='Controls:', x=-0.8, y=0.24, scale=1.2, color=color.white)
        self.controls_text_2 = Text(text='Movement: WASD', x=-0.8, y=0.20, scale=0.6, color=color.white)
        self.controls_text_3 = Text(text='Fast Acceleration: SHIFT', x=-0.8, y=0.18, scale=0.6, color=color.white)
        self.controls_text_4 = Text(text='Handbrake: SPACE', x=-0.8, y=0.16, scale=0.6, color=color.white)
        self.controls_text_5 = Text(text='Extreme Drift Mode: P', x=-0.8, y=0.14, scale=0.6, color=color.white)

        # ---------------- CAMERA SETUP ----------------
        camera.parent = self # Parent camera to the car for chase effect
        camera.position = (0, 6, -36) # Position relative to the car
        camera.rotation_x = 5.5 # Angle camera down
        camera.fov = 110 # Field of view

    def update(self):
        # Current speed and forward direction
        current_speed_magnitude = self.rigid_body.getLinearVelocity().length()
        dot_forward = self.rigid_body.getLinearVelocity().normalized().dot(self.forward) if current_speed_magnitude > 0.1 else 0
        is_moving_forward = dot_forward > 0.1
        current_max_speed_for_gear = self.gear_data[self.current_gear]['max_speed_for_gear']

        # ---------------- AUTOMATIC GEAR SHIFTING ----------------
        if is_moving_forward and self.current_gear < self.max_forward_gear:
            if current_speed_magnitude >= self.gear_data[self.current_gear]['upshift_speed']:
                self.current_gear += 1
        elif is_moving_forward and self.current_gear > 1:
            if current_speed_magnitude < self.gear_data[self.current_gear]['downshift_speed']:
                self.current_gear -= 1
        elif current_speed_magnitude < 1.0:
            if held_keys['s'] and not is_moving_forward:
                self.current_gear = 0
            elif not held_keys['w'] and not held_keys['s'] and not held_keys['space']:
                self.current_gear = 1
                self.rigid_body.setLinearVelocity(Vec3(0,0,0))

        # ---------------- DYNAMIC PHYSICS ADJUSTMENTS ----------------
        # Initialize current physics parameters
        current_engine_thrust_force = self.engine_thrust_force
        current_braking_force = self.braking_force
        current_reverse_thrust_force = self.reverse_thrust_force
        current_handbrake_braking_force = self.handbrake_braking_force
        current_turn_torque_strength = self.base_turn_torque_strength
        current_angular_drag_torque = self.base_angular_drag_torque
        current_rolling_resistance_force = self.rolling_resistance_force

        # Determine grip and angular drag based on extreme drift mode
        actual_sideways_grip_factor = self.base_grip_factor
        actual_angular_drag_reduction_factor = 1.0

        if self.is_extreme_drift_mode:
            actual_sideways_grip_factor = self.extreme_drift_grip_factor
            current_turn_torque_strength *= self.extreme_drift_turn_boost
            actual_angular_drag_reduction_factor = self.extreme_drift_angular_drag_reduction

        # Apply Boost multipliers if Shift is held
        if held_keys["shift"]:
            current_engine_thrust_force *= self.boost_multiplier
            current_braking_force *= self.boost_multiplier
            current_reverse_thrust_force *= self.boost_multiplier
            current_handbrake_braking_force *= self.boost_multiplier
            current_turn_torque_strength *= self.boost_multiplier
            current_angular_drag_torque *= 0.75
            actual_sideways_grip_factor *= 0.75
            current_max_speed_for_gear *= self.boost_multiplier

        # ---------------- HANDBRAKE LOGIC ----------------
        if held_keys['space']:
            self.handbrake_active = True
            self.rigid_body.apply_central_force(-self.rigid_body.getLinearVelocity().normalized() * current_handbrake_braking_force)
            self.current_sideways_grip = actual_sideways_grip_factor * self.handbrake_friction_loss_factor
            current_rolling_resistance_force *= 0.2
        else:
            self.handbrake_active = False
            target_grip = actual_sideways_grip_factor
            self.current_sideways_grip = lerp(
                self.current_sideways_grip,
                target_grip,
                time.dt * self.drift_recover_rate
            )
            self.current_sideways_grip = clamp(self.current_sideways_grip, self.extreme_drift_grip_factor * 0.5, self.base_grip_factor * 1.5)

        # ---------------- ENGINE THRUST AND BRAKING ----------------
        if held_keys['w']:
            speed_ratio_in_gear = min(1, current_speed_magnitude / current_max_speed_for_gear)
            effective_thrust = current_engine_thrust_force * self.gear_data[self.current_gear]['thrust_multiplier'] * (1 - speed_ratio_in_gear)
            self.rigid_body.apply_force(self.forward * effective_thrust, Vec3(0,0,0))
        elif held_keys['s'] and not held_keys['space']:
            if dot_forward > 0.1:
                self.rigid_body.apply_force(-self.forward * current_braking_force, Vec3(0,0,0))
            else:
                speed_ratio_reverse = min(1, current_speed_magnitude / self.max_reverse_speed)
                effective_reverse_thrust = current_reverse_thrust_force * (1 - speed_ratio_reverse)
                self.rigid_body.apply_force(-self.forward * effective_reverse_thrust, Vec3(0,0,0))

        # ---------------- STEERING INPUT AND TURNING ----------------
        target_steering_input = 0.0
        if held_keys['d']:
            target_steering_input = self.max_steering_angle_input
        elif held_keys['a']:
            target_steering_input = -self.max_steering_angle_input

        lerp_speed = self.steering_speed if target_steering_input != 0 else self.steering_return_speed
        self.current_steering_input = lerp(self.current_steering_input, target_steering_input, time.dt * lerp_speed)
        self.current_steering_input = clamp(self.current_steering_input, -self.max_steering_angle_input, self.max_steering_angle_input)

        turn_speed_factor_normalized = min(1, current_speed_magnitude / self.turn_torque_speed_scaling_max_speed)
        speed_scaled_turn_factor = lerp(self.turn_torque_max_speed_factor, self.turn_torque_min_speed_factor, turn_speed_factor_normalized)

        local_sideways_speed = self.rigid_body.getLinearVelocity().dot(self.right)
        drift_assist_factor = 1 + (abs(local_sideways_speed) / current_speed_magnitude) * 1.2 if current_speed_magnitude > 0.1 else 1.0

        if abs(self.current_steering_input) > 0.01:
            non_linear_steering_input = math.copysign(
                math.pow(abs(self.current_steering_input), self.steering_non_linear_power),
                self.current_steering_input
            )
            applied_torque = current_turn_torque_strength * drift_assist_factor * speed_scaled_turn_factor * non_linear_steering_input
            self.rigid_body.apply_torque((0, applied_torque, 0))

        # ---------------- ANGULAR DAMPING AND CAP ----------------
        angular_vel_y = self.rigid_body.getAngularVelocity().y
        angular_vel_magnitude = abs(angular_vel_y)

        if angular_vel_magnitude > 0.1:
            speed_scaled_angular_drag_multiplier = 1 + (current_speed_magnitude * self.angular_drag_speed_scaling_factor)
            effective_angular_drag = current_angular_drag_torque * actual_angular_drag_reduction_factor * speed_scaled_angular_drag_multiplier
            self.rigid_body.apply_torque((0, -angular_vel_y * effective_angular_drag, 0))
        else:
            self.rigid_body.setAngularVelocity(Vec3(0,0,0))

        if angular_vel_magnitude > self.max_angular_velocity_y:
            self.rigid_body.apply_torque((0, -math.copysign(self.angular_velocity_cap_force, angular_vel_y), 0))

        # ---------------- AIR AND ROLLING RESISTANCE ----------------
        if current_speed_magnitude > 0.05:
            air_resistance_force = self.air_resistance_factor * current_speed_magnitude**2
            self.rigid_body.apply_central_force(-self.rigid_body.getLinearVelocity().normalized() * air_resistance_force)
            self.rigid_body.apply_central_force(-self.rigid_body.getLinearVelocity().normalized() * current_rolling_resistance_force)

            # --- Sideways Friction Logic ---
            local_sideways_speed = self.rigid_body.getLinearVelocity().dot(self.right)
            actual_sideways_velocity = self.right * local_sideways_speed

            sideways_friction_force_magnitude = abs(local_sideways_speed) * self.sideways_friction_multiplier * self.current_sideways_grip
            sideways_friction_force_magnitude = min(sideways_friction_force_magnitude, self.engine_thrust_force * 3)

            if abs(local_sideways_speed) > 0.01:
                self.rigid_body.apply_central_force(-actual_sideways_velocity.normalized() * sideways_friction_force_magnitude)
            else:
                if self.rigid_body.getLinearVelocity().dot(self.right) != 0:
                    self.rigid_body.apply_central_force(-self.right * self.rigid_body.getLinearVelocity().dot(self.right) * (self.rigid_body.getMass() / time.dt))

            # Coasting Friction
            if not held_keys['w'] and not held_keys['s'] and not held_keys['space']:
                if abs(current_speed_magnitude) > 0.05:
                    coast_friction_force = current_rolling_resistance_force * (min(1, current_speed_magnitude / current_max_speed_for_gear)**2) * 15
                    self.rigid_body.apply_central_force(-self.forward * coast_friction_force)
                elif current_speed_magnitude < 0.5:
                    self.rigid_body.setLinearVelocity(Vec3(0,0,0))
        else:
            self.rigid_body.setLinearVelocity(Vec3(0,0,0))

        # ---------------- SPEED LIMITING ----------------
        current_speed_magnitude_after_forces = self.rigid_body.getLinearVelocity().length()
        if current_speed_magnitude_after_forces > 0.1:
            dot_overall_vs_car_forward = self.rigid_body.getLinearVelocity().normalized().dot(self.forward)

            if dot_overall_vs_car_forward > 0:
                if current_speed_magnitude_after_forces > current_max_speed_for_gear:
                    self.rigid_body.setLinearVelocity(self.rigid_body.getLinearVelocity().normalized() * current_max_speed_for_gear)
            elif dot_overall_vs_car_forward < 0:
                max_reverse_speed_effective = self.max_reverse_speed * (self.boost_multiplier if held_keys["shift"] else 1)
                if current_speed_magnitude_after_forces > max_reverse_speed_effective:
                    self.rigid_body.setLinearVelocity(self.rigid_body.getLinearVelocity().normalized() * max_reverse_speed_effective)
        else:
            self.rigid_body.setLinearVelocity(Vec3(0,0,0))

        # ---------------- GUI UPDATES ----------------
        self.speed_text.text = f'Speed: {current_speed_magnitude_after_forces:.1f} units/s'
        if self.current_gear == 0:
            self.gear_text.text = 'Gear: R'
        elif self.current_gear == 1 and current_speed_magnitude_after_forces < 1.0 and not held_keys['w'] and not held_keys['s'] and not held_keys['space']:
            self.gear_text.text = 'Gear: N'
        else:
            self.gear_text.text = f'Gear: {self.current_gear}'
        self.drift_mode_text.text = f'Extreme Drift Mode: {"ON" if self.is_extreme_drift_mode else "OFF"}'

    def input(self, key):
        # Toggle Extreme Drift Mode
        if key == 'p':
            self.is_extreme_drift_mode = not self.is_extreme_drift_mode
            print(f"Extreme Drift Mode: {'ON' if self.is_extreme_drift_mode else 'OFF'}")
