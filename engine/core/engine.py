import os
import math

from engine.platform.windows.window import Window
from engine.platform.windows.gpu_context import GPUContext
from engine.graphics.renderer import Renderer
from engine.core.game_loop import GameLoop
from engine.core.time import Time
from engine.platform.windows.input import Input
from engine.graphics.camera.camera import Camera
from engine.math.vector import Vector3
from engine.graphics.shaders.shader import Shader
from engine.math.transform import Transform
from engine.world.world import World
from engine.world.world_manager import WorldManager
from engine.world.world_renderer import WorldRenderer
from engine.physics.physics_world import PhysicsWorld
from engine.physics.character_controller import CharacterController
from engine.physics.vehicle import Vehicle
from engine.world.world_object_manager import WorldObjectManager
from engine.world.world_object_renderer import WorldObjectRenderer


class Engine:
    def __init__(
        self,
        title="Viktor3D - GTA 6 Prototype",
        width=1280,
        height=720,
        target_fps=60,
        gl_major=3,
        gl_minor=3
    ):
        self.title = title
        self.width = width
        self.height = height
        self.target_fps = target_fps
        self.gl_major = gl_major
        self.gl_minor = gl_minor

        self.window = None
        self.gpu = None
        self.renderer = None
        self.game_loop = None
        self.shader = None
        self.input = None
        self.camera = None

        self.world = None
        self.world_manager = None
        self.world_renderer = None
        self.world_transform = None
        self.world_object_manager = None
        self.world_object_renderer = None

        self.physics_world = None
        self.player = None
        self.vehicles = []
        self.active_vehicle = None

        self.time_of_day = 16.5  # Aranyóra / Vice City naplemente
        self.mouse_locked = True

        self.initialized = False
        self.running = False
        self.clear_color = (0.95, 0.55, 0.38, 1.0)

    def initialize(self):
        if self.initialized:
            return

        self.window = Window(title=self.title, width=self.width, height=self.height)
        self.input = Input()
        self.input.set_mouse_locked(
            self.window.hwnd,
            True,
            self.width,
            self.height
        )

        self.camera = Camera(
            position=Vector3(0.0, 2.0, 0.0),
            fov=72.0,
            aspect_ratio=self.width / self.height,
            near=0.1,
            far=600.0
        )

        self.gpu = GPUContext(self.window, major=self.gl_major, minor=self.gl_minor)
        self.renderer = Renderer(self.gpu)
        self.renderer.set_clear_color(*self.clear_color)

        # Nagyobb nyílt világ (768x768 egység)
        self.world = World(chunk_size=64.0, chunks_x=12, chunks_z=12)
        self.world_manager = WorldManager(self.world, load_radius=2)
        self.world_renderer = WorldRenderer(self.gpu, self.world_manager)

        self.world_object_manager = WorldObjectManager()
        self.world_object_renderer = WorldObjectRenderer(self.renderer)

        self.physics_world = PhysicsWorld()
        self.player = CharacterController(
            physics_world=self.physics_world,
            terrain_generator=self.world_renderer.terrain_generator,
            city_generator=self.world_renderer.city_generator,
            position=Vector3(0.0, 0.0, 6.0),
            walk_speed=6.5,
            sprint_speed=13.0,
            jump_strength=8.5,
            acceleration=24.0,
            deceleration=30.0,
            eye_height=1.65,
            collision_radius=0.45
        )

        self.camera.position = self.player.get_camera_position()

        self.player.camera_orbit_yaw = self.camera.yaw
        self.player.camera_orbit_pitch = -12.0

        self.player.update_camera(self.camera, 1.0 / 60.0)

        self.camera.position = self.player.get_camera_position()
        self.world_transform = Transform()

        self.world_manager.update(self.camera.position.x, self.camera.position.z)
        self.world_renderer.update()

        # Járművek lerakása az utakra (1 sportautó közelünkben + AI forgalom)
        tg = self.world_renderer.terrain_generator
        cg = self.world_renderer.city_generator
        car_specs = [
            (0.0, -4.0, (0.95, 0.12, 0.25), False),
            (64.0, 0.0, (0.10, 0.75, 0.95), True),
            (-64.0, 64.0, (0.95, 0.80, 0.10), True),
            (0.0, -64.0, (0.85, 0.85, 0.90), True),
        ]
        for cx, cz, col, ai in car_specs:
            gy = tg.get_height(cx, cz)
            v = Vehicle(self.gpu, tg, cg, Vector3(cx, gy, cz), color=col, is_ai=ai)
            self.vehicles.append(v)

        # Shaders betöltése
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        shader_dir = os.path.join(base_dir, "engine", "graphics", "shaders")
        with open(os.path.join(shader_dir, "basic.vert"), "r", encoding="utf-8") as f:
            vert_src = f.read()
        with open(os.path.join(shader_dir, "basic.frag"), "r", encoding="utf-8") as f:
            frag_src = f.read()

        self.shader = Shader(self.gpu, vert_src, frag_src)
        self.game_loop = GameLoop(self, target_fps=self.target_fps)
        self.initialized = True
        print("[Viktor3D GTA6] Irányítás: WASD mozgás/vezetés | SHIFT sprint | SPACE ugrás/kézifék | F autóba be/ki | T napszak | TAB egér")

    def _get_atmosphere(self):
        # Napszak (0..24 óra) -> égbolt, napfény irány és köd
        angle = ((self.time_of_day - 6.0) / 24.0) * math.pi * 2.0
        sun_y = math.sin(angle)
        sun_x = math.cos(angle)
        light_dir = (-sun_x, -max(0.15, sun_y), -0.35)

        if sun_y > 0.25:
            # Nappal (trópusi kék ég)
            sky = (0.35, 0.68, 0.96)
            light = (1.0, 0.97, 0.90)
            ambient = (0.38, 0.42, 0.48)
        elif sun_y > -0.15:
            # Naplemente (Vice City narancs-lila)
            sky = (0.94, 0.48, 0.36)
            light = (1.0, 0.62, 0.38)
            ambient = (0.34, 0.24, 0.30)
        else:
            # Éjszaka (neon városfények)
            sky = (0.04, 0.06, 0.14)
            light = (0.22, 0.28, 0.48)
            ambient = (0.14, 0.16, 0.24)

        return sky, light_dir, light, ambient

    def update(self, delta_time):
        if (
            self.camera is None
            or self.input is None
            or self.player is None
        ):
            return

        # ======================================
        # INPUT
        # ======================================

        # Fontos:
        # Az Input.update() már a GameLoop-ban fut.
        # Itt nem szabad másodszor meghívni!

        if self.input.is_key_pressed(0x1B):  # ESC
            self.window.running = False
            return

        # ======================================
        # MOUSE LOCK
        # ======================================

        if self.input.is_key_pressed(0x09):  # TAB

            self.mouse_locked = not self.mouse_locked

            self.input.set_mouse_locked(
                self.window.hwnd,
                self.mouse_locked,
                self.width,
                self.height
            )

        # ======================================
        # TIME OF DAY
        # ======================================

        if self.input.is_key_down(0x54):  # T

            self.time_of_day = (
                self.time_of_day + delta_time * 3.0
            ) % 24.0

        else:

            self.time_of_day = (
                self.time_of_day + delta_time * 0.08
            ) % 24.0

        # ======================================
        # CAMERA MOUSE INPUT
        # ======================================

        if self.mouse_locked:

            dx, dy = self.input.get_mouse_delta()

            if self.active_vehicle is not None:

                self.camera.rotate(dx, dy)

            else:

                self.player.rotate_camera(
                    dx,
                    dy,
                    sensitivity=self.camera.sensitivity
                )

            self.input.set_mouse_position(
                self.window.hwnd,
                self.width // 2,
                self.height // 2
            )

        # ======================================
        # ENTER / EXIT VEHICLE
        # ======================================

        if self.input.is_key_pressed(0x46):  # F

            if self.active_vehicle is not None:

                exit_position = (
                    self.active_vehicle.transform.position
                    + Vector3(2.2, 0.2, 0.0)
                )

                self.player.teleport(exit_position)

                self.active_vehicle.driver = None
                self.active_vehicle = None

            else:

                player_position = self.player.get_position()

                for vehicle in self.vehicles:

                    distance = player_position.distance(
                        vehicle.transform.position
                    )

                    if distance < 4.5:

                        self.active_vehicle = vehicle
                        vehicle.driver = self.player
                        vehicle.is_ai = False

                        break

        # ======================================
        # VEHICLE UPDATE
        # ======================================

        for vehicle in self.vehicles:

            vehicle.update(
                self.input,
                delta_time
            )

        # ======================================
        # PLAYER / VEHICLE CAMERA
        # ======================================

        if self.active_vehicle is not None:

            car_position = (
                self.active_vehicle.transform.position
            )

            self.player.position = car_position.copy()

            camera_offset = (
                self.camera.front * -7.5
                + Vector3(0.0, 2.8, 0.0)
            )

            self.camera.position = (
                car_position + camera_offset
            )

        else:

            self.player.update(
                self.input,
                self.camera,
                delta_time
            )

            self.player.update_camera(
                self.camera,
                delta_time
            )

        # ======================================
        # WORLD BOUNDARIES
        # ======================================

        player_position = self.player.get_position()

        player_position.x = max(
            -self.world.half_width + 1.0,
            min(self.world.half_width - 1.0, player_position.x)
        )

        player_position.z = max(
            -self.world.half_depth + 1.0,
            min(self.world.half_depth - 1.0, player_position.z)
        )

        self.player.position.x = player_position.x
        self.player.position.z = player_position.z

        # ======================================
        # CHUNK MANAGEMENT
        # ======================================

        current_chunk = self.world.world_to_chunk(
            player_position.x,
            player_position.z
        )

        # Update required chunks only when entering another chunk
        if current_chunk != self.world_manager.player_chunk:

            self.world_manager.update(
                player_position.x,
                player_position.z
            )

        # Process the generation queue every frame
        self.world_renderer.update()

        # ======================================
        # WORLD OBJECTS
        # ======================================

        self.world_object_manager.update(delta_time)

    def render(self):
        if self.shader is None:
            return

        sky, light_dir, light_col, ambient_col = self._get_atmosphere()
        self.renderer.set_clear_color(sky[0], sky[1], sky[2], 1.0)

        self.shader.use()
        self.shader.set_vector3("uLightDir", *light_dir)
        self.shader.set_vector3("uLightColor", *light_col)
        self.shader.set_vector3("uAmbientColor", *ambient_col)
        self.shader.set_vector3("uFogColor", *sky)
        self.shader.set_float("uFogDensity", 0.0045)
        self.shader.set_vector3("uCameraPos", self.camera.position.x, self.camera.position.y, self.camera.position.z)

        self.world_renderer.render(
            self.renderer,
            self.shader,
            self.camera,
            self.world_transform.get_matrix()
        )

        # Járművek kirajzolása
        for v in self.vehicles:
            self.shader.set_matrix4("uModel", v.transform.get_matrix())
            self.shader.set_vector4("uColor", 1.0, 1.0, 1.0, 1.0)
            self.renderer.draw_mesh(v.mesh, self.shader)

        self.world_object_renderer.render(
            self.world_object_manager,
            self.shader,
            self.camera
        )

    def run(self):
        if self.running:
            return
        self.initialize()
        if not self.initialized:
            return
        self.running = True
        try:
            self.game_loop.run()
        finally:
            self.running = False
            self.shutdown()

    def set_clear_color(self, red, green, blue, alpha=1.0):
        self.clear_color = (float(red), float(green), float(blue), float(alpha))
        if self.renderer is not None:
            self.renderer.set_clear_color(*self.clear_color)

    def shutdown(self):
        if self.game_loop is not None:
            self.game_loop.stop()
        for v in self.vehicles:
            v.close()
        self.vehicles.clear()
        if self.player is not None:
            self.player.close()
        if self.physics_world is not None:
            self.physics_world.close()
        if self.world_object_renderer is not None:
            self.world_object_renderer.close()
        if self.world_object_manager is not None:
            self.world_object_manager.close()
        if self.world_renderer:
            self.world_renderer.close()
        if self.world_manager:
            self.world_manager.unload_all()
        if self.shader is not None:
            self.shader.close()
        if self.renderer is not None:
            self.renderer.close()
        if self.gpu is not None:
            self.gpu.close()
        if self.window is not None:
            self.window.close()
        self.initialized = False
        self.running = False