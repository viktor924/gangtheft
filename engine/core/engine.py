
import os

from engine.platform.windows.window import Window
from engine.platform.windows.gpu_context import GPUContext
from engine.graphics.renderer import Renderer
from engine.core.game_loop import GameLoop
from engine.core.time import Time
from engine.platform.windows.input import Input
from engine.graphics.camera.camera import Camera
from engine.math.vector import Vector3
from engine.graphics.shaders.shader import Shader
from engine.graphics.mesh import Mesh
from engine.math.transform import Transform
from engine.world.world import World
from engine.world.world_manager import WorldManager
from engine.world.world_renderer import WorldRenderer
from engine.physics.physics_world import PhysicsWorld
from engine.physics.character_controller import CharacterController


class Engine:
    def __init__(
        self,
        title="Viktor3D Engine",
        width=1280,
        height=720,
        target_fps=0,
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
        self.mesh = None
        self.transform = None
        self.input = None
        self.camera = None
        self.world = None
        self.world_manager = None
        self.world_renderer = None
        self.world_transform = None

        self.physics_world = None
        self.player = None

        self.initialized = False
        self.running = False

        self.clear_color = (0.08, 0.12, 0.20, 1.0)

    def initialize(self):
        if self.initialized:
            return

        print("================================")
        print("       VIKTOR3D ENGINE")
        print("================================")

        try:
            # Windows ablak létrehozása
            print("[Engine] Creating window...")

            self.window = Window(
                title=self.title,
                width=self.width,
                height=self.height
            )

            # Input létrehozása
            self.input = Input()

            # Camera létrehozása
            self.camera = Camera(
                position=Vector3(0.0, 1.8, 3.0),
                fov=70.0,
                aspect_ratio=self.width / self.height
            )

            # Initial world view
            self.camera.position = Vector3(0.0, 3.0, 8.0)
            self.camera.pitch = -15.0
            self.camera.update_vectors()

            print("[Engine] Camera initialized.")

            # GPU kontextus létrehozása
            print("[Engine] Initializing GPU...")

            self.gpu = GPUContext(
                self.window,
                major=self.gl_major,
                minor=self.gl_minor
            )

            self.gpu.print_information()

            # Renderer létrehozása
            print("[Engine] Initializing renderer...")

            self.renderer = Renderer(self.gpu)
            self.renderer.set_clear_color(*self.clear_color)

            # ======================================
            # WORLD SYSTEM
            # ======================================

            print("[Engine] Initializing world...")

            self.world = World(
                chunk_size=64.0,
                chunks_x=8,
                chunks_z=8
            )

            self.world_manager = WorldManager(
                self.world,
                load_radius=1
            )

            self.world_renderer = WorldRenderer(
                self.gpu,
                self.world_manager
            )

            # ======================================
            # PHYSICS SYSTEM
            # ======================================

            print("[Engine] Initializing physics...")

            self.physics_world = PhysicsWorld()

            self.player = CharacterController(
                physics_world=self.physics_world,
                terrain_generator=self.world_renderer.terrain_generator,
                position=Vector3(
                    self.camera.position.x,
                    0.0,
                    self.camera.position.z
                ),
                walk_speed=5.0,
                sprint_speed=10.0,
                jump_strength=8.0,
                eye_height=1.8
            )

            # Attach camera to player
            self.camera.position = self.player.get_camera_position()

            print("[Engine] Physics system initialized.")

            self.world_transform = Transform(
                position=Vector3(0.0, 0.0, 0.0),
                rotation=Vector3(0.0, 0.0, 0.0),
                scale=Vector3(1.0, 1.0, 1.0)
            )

            # Load initial chunks
            self.world_manager.update(
                self.camera.position.x,
                self.camera.position.z
            )

            self.world_renderer.update()

            print("[Engine] World system initialized.")

            # Shader inicializálása
            print("[Engine] Loading shaders...")

            base_dir = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
            )

            shader_dir = os.path.join(
                base_dir,
                "engine",
                "graphics",
                "shaders"
            )

            with open(
                os.path.join(shader_dir, "basic.vert"),
                "r",
                encoding="utf-8"
            ) as file:
                vertex_source = file.read()

            with open(
                os.path.join(shader_dir, "basic.frag"),
                "r",
                encoding="utf-8"
            ) as file:
                fragment_source = file.read()

            self.shader = Shader(
                self.gpu,
                vertex_source,
                fragment_source
            )

            # Első háromszög Mesh
            print("[Engine] Creating first mesh...")

            # 24 vertices - 4 vertices per face
            vertices = [
                # Front
                -0.75, -0.75,  0.75,
                0.75, -0.75,  0.75,
                0.75,  0.75,  0.75,
                -0.75,  0.75,  0.75,

                # Back
                0.75, -0.75, -0.75,
                -0.75, -0.75, -0.75,
                -0.75,  0.75, -0.75,
                0.75,  0.75, -0.75,

                # Left
                -0.75, -0.75, -0.75,
                -0.75, -0.75,  0.75,
                -0.75,  0.75,  0.75,
                -0.75,  0.75, -0.75,

                # Right
                0.75, -0.75,  0.75,
                0.75, -0.75, -0.75,
                0.75,  0.75, -0.75,
                0.75,  0.75,  0.75,

                # Top
                -0.75,  0.75,  0.75,
                0.75,  0.75,  0.75,
                0.75,  0.75, -0.75,
                -0.75,  0.75, -0.75,

                # Bottom
                -0.75, -0.75, -0.75,
                0.75, -0.75, -0.75,
                0.75, -0.75,  0.75,
                -0.75, -0.75,  0.75,
            ]

            indices = []

            for face in range(6):
                base = face * 4
                indices.extend([
                    base, base + 1, base + 2,
                    base + 2, base + 3, base
                ])

            # Face colors: Red, Green, Blue, Yellow, Orange, Purple

            face_colors = [
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
                (0.0, 0.0, 1.0),
                (1.0, 1.0, 0.0),
                (1.0, 0.5, 0.0),
                (0.7, 0.0, 1.0),
            ]

            colors = []

            for face_color in face_colors:
                for _ in range(4):
                    colors.extend(face_color)

            self.mesh = Mesh(
                self.gpu,
                vertices,
                indices,
                colors
            )

            # Objektum transzformáció
            self.transform = Transform(
                position=Vector3(0.0, 1.8, 0.0),
                rotation=Vector3(0.0, 0.0, 0.0),
                scale=Vector3(1.0, 1.0, 1.0)
            )

            # Game Loop létrehozása
            print("[Engine] Initializing game loop...")

            self.game_loop = GameLoop(
                self,
                target_fps=self.target_fps
            )

            self.initialized = True

            print("[Engine] Initialization complete!")

        except Exception:
            self.shutdown()
            raise

    
    def update(self, delta_time):

        if (
            self.camera is None
            or self.input is None
            or self.player is None
        ):
            return

        # ======================================
        # CAMERA ROTATION
        # ======================================

        mouse_dx, mouse_dy = self.input.get_mouse_delta()

        self.camera.rotate(
            mouse_dx,
            mouse_dy,
            sensitivity=0.1
        )

        # ======================================
        # PLAYER MOVEMENT AND PHYSICS
        # ======================================

        self.player.update(
            self.input,
            self.camera,
            delta_time
        )

        # ======================================
        # WORLD BOUNDARIES
        # ======================================

        player_position = self.player.get_position()

        player_position.x = max(
            -self.world.half_width + 0.1,
            min(
                self.world.half_width - 0.1,
                player_position.x
            )
        )

        player_position.z = max(
            -self.world.half_depth + 0.1,
            min(
                self.world.half_depth - 0.1,
                player_position.z
            )
        )

        # ======================================
        # WORLD CHUNK UPDATE
        # ======================================

        current_chunk = self.world.world_to_chunk(
            player_position.x,
            player_position.z
        )

        if current_chunk != self.world_manager.player_chunk:

            self.world_manager.update(
                player_position.x,
                player_position.z
            )

            self.world_renderer.update()

        # ======================================
        # CAMERA FOLLOW
        # ======================================

        self.camera.position = self.player.get_camera_position()

        # ======================================
        # DEBUG
        # ======================================

        if self.input.is_key_pressed(0x50):

            print("[Player] Position:", self.player.get_position())
            print("[Player] Grounded:", self.player.is_on_ground())

            print("[Camera] Position:", self.camera.position)
            print("[Camera] Yaw:", self.camera.yaw)
            print("[Camera] Pitch:", self.camera.pitch)

        # ======================================
        # CUBE ROTATION
        # ======================================

        if self.transform is not None:

            self.transform.rotate(
                Vector3(
                    45.0 * delta_time,
                    60.0 * delta_time,
                    30.0 * delta_time
                )
            )


    def render(self):
        if (
            self.shader is None
            or self.mesh is None
            or self.transform is None
        ):
            return

        self.shader.use()

        self.shader.set_matrix4(
            "uModel",
            self.transform.get_matrix()
        )

        self.shader.set_matrix4(
            "uView",
            self.camera.get_view_matrix()
        )

        self.shader.set_matrix4(
            "uProjection",
            self.camera.get_projection_matrix()
        )

        self.shader.set_vector4(
            "uColor",
            1.0,
            1.0,
            1.0,
            1.0
        )

        self.renderer.draw_mesh(
            self.mesh,
            self.shader
        )

        # ======================================
        # RENDER WORLD
        # ======================================

        self.world_renderer.render(
            self.renderer,
            self.shader,
            self.camera,
            self.world_transform.get_matrix()
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
        self.clear_color = (
            float(red),
            float(green),
            float(blue),
            float(alpha)
        )

        if self.renderer is not None:
            self.renderer.set_clear_color(*self.clear_color)

    def set_target_fps(self, fps):
        self.target_fps = max(0, int(fps))

        if self.game_loop is not None:
            self.game_loop.set_target_fps(self.target_fps)

    def shutdown(self):
        print("[Engine] Shutting down...")

        if self.game_loop is not None:
            self.game_loop.stop()

        if self.mesh is not None:
            self.mesh.close()
            self.mesh = None

        if self.player is not None:
            self.player.close()
            self.player = None

        if self.physics_world is not None:
            self.physics_world.close()
            self.physics_world = None

        if self.world_renderer:
            self.world_renderer.close()

        if self.world_manager:
            self.world_manager.unload_all()

        if self.shader is not None:
            self.shader.close()
            self.shader = None

        if self.renderer is not None:
            self.renderer.close()
            self.renderer = None

        if self.gpu is not None:
            self.gpu.close()
            self.gpu = None

        if self.window is not None:
            self.window.close()
            self.window = None

        self.initialized = False
        self.running = False

        print("[Engine] Shutdown complete.")