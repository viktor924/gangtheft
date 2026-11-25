# Viktor3D Engine

**A custom 3D game engine built from scratch using Python, Win32 API, WGL, and OpenGL 3.3.**

Viktor3D is an experimental, independently developed 3D game engine designed to explore low-level graphics programming, engine architecture, procedural world generation, and real-time 3D rendering.

The engine is being developed from the ground up, with custom systems for rendering, mathematics, camera control, input handling, physics, terrain generation, world management, and game objects.

The long-term goal is to create a modular and extensible engine capable of supporting large-scale, GTA-inspired open-world environments.

> **Project Status:** Active Development  
> **Platform:** Windows  
> **Graphics API:** OpenGL 3.3 Core Profile  
> **Language:** Python

---

## Features

### Core Engine
- Custom Windows application window.
- Direct Win32 API integration through Python `ctypes`.
- OpenGL context creation using WGL.
- Custom engine initialization and shutdown.
- Main game loop.
- Delta time management.
- Resource lifecycle management.

### Graphics System
- Custom OpenGL renderer.
- GLSL vertex and fragment shaders.
- Shader compilation and linking.
- Uniform variable management.
- VAO, VBO, and EBO management.
- GPU mesh uploading and rendering.
- Indexed triangle rendering.
- Per-vertex color support.
- Multiple independently rendered 3D objects.

### Camera System
- First-person camera.
- Mouse-controlled camera rotation.
- Yaw and pitch handling.
- Forward, right, and direction vectors.
- View matrix generation.
- Perspective projection matrix.

### Input System
- Keyboard input handling.
- Mouse movement detection.
- Key press detection.
- Continuous key state detection.
- Windows virtual key integration.

Current controls:

| Key | Action |
|---|---|
| W | Move forward |
| S | Move backward |
| A | Move left |
| D | Move right |
| Shift | Sprint |
| Space | Jump |
| Mouse | Look around |

### Mathematics System
Custom mathematical modules developed specifically for the engine.

Implemented components:
- Vector2
- Vector3
- Vector4
- Matrix3
- Matrix4
- Transform

Transform functionality:
- Position management.
- Rotation management.
- Scale management.
- Translation and rotation operations.
- Transformation matrix generation.
- Cached transformation matrices.
- Dirty flag optimization.
- Direction vectors.
- Look-at functionality.

### World System
A custom chunk-based world management system.

Current world configuration:

| Property | Value |
|---|---:|
| World width | 512 meters |
| World depth | 512 meters |
| Chunk size | 64 × 64 meters |
| Chunks along X | 8 |
| Chunks along Z | 8 |
| Total chunks | 64 |
| Default loading radius | 1 chunk |

Implemented functionality:
- World coordinate management.
- World-to-chunk conversion.
- Chunk creation and unloading.
- Player-centered chunk streaming.
- Active chunk tracking.
- World boundary detection.

The current streaming configuration loads a 3 × 3 chunk area around the player.

### Procedural Terrain Generation
The terrain system uses custom deterministic noise generation.

Implemented features:
- Seed-based terrain generation.
- Hash-based noise.
- Smooth interpolation.
- Linear interpolation.
- Fractal Brownian Motion (FBM).
- Multi-octave noise generation.
- World-coordinate-based height calculation.

The same seed and world coordinates produce consistent terrain heights.

### Physics System
A custom foundational physics system.

Currently implemented:
- Gravity simulation.
- Terminal velocity.
- Vertical velocity calculation.
- Basic ground collision resolution.
- Ground detection.

Current default physics values:

| Property | Value |
|---|---:|
| Gravity | -24.0 |
| Terminal velocity | -50.0 |

### Character Controller
A custom first-person character controller.

Implemented functionality:
- WASD movement.
- Sprinting.
- Jumping.
- Gravity.
- Ground detection.
- Terrain height following.
- Basic air control.
- Camera attachment to the player.

Current movement configuration:

| Property | Value |
|---|---:|
| Walking speed | 5.0 |
| Sprint speed | 10.0 |
| Jump strength | 8.0 |
| Camera eye height | 1.8 meters |
| Air control | 0.65 |

### Game Object System
A modular object management and rendering system.

#### GameObject
Each game object contains:
- Unique ID.
- Object name.
- Mesh reference.
- Transform.
- Color.
- Visibility state.
- Active state.
- Initialization state.

Supported operations:
- Object creation.
- Mesh assignment.
- Position, rotation, and scale management.
- Color modification.
- Visibility control.
- Active state control.
- Object cleanup.

#### WorldObjectManager
Manages game objects inside the world.

Implemented functionality:
- Add objects.
- Create objects.
- Remove objects.
- Find objects by ID.
- Find objects by name.
- Retrieve all objects.
- Retrieve active objects.
- Retrieve visible objects.
- Update managed objects.
- Object statistics.
- Complete object cleanup.

#### WorldObjectRenderer
Responsible for rendering managed game objects.

Implemented functionality:
- Retrieve objects from the object manager.
- Individual model matrices.
- Camera view and projection matrices.
- Individual object colors.
- Mesh rendering.
- Skip inactive objects.
- Skip invisible objects.
- Skip objects without meshes.
- Rendering statistics.

The object rendering system is already integrated into the main engine.

A separately created GameObject is successfully rendered in the world alongside the original test cube.

---

## Project Structure

```text
Viktor3D/
│
├── engine/
│   │
│   ├── audio/
│   │
│   ├── core/
│   │
│   ├── graphics/
│   │   ├── camera/
│   │   └── shaders/
│   │
│   ├── math/
│   │
│   ├── physics/
│   │
│   ├── platform/
│   │   └── windows/
│   │
│   ├── resources/
│   │
│   ├── ui/
│   │
│   └── world/
│
├── tests/
│
└── run.py
```

The engine follows a modular architecture. Individual systems are separated into dedicated modules to simplify development, testing, maintenance, and future expansion.

---

## Requirements

Current development environment:

- Windows 10 or Windows 11.
- Python 3.
- GPU supporting OpenGL 3.3 Core Profile.
- Compatible graphics drivers.

The engine currently targets Windows only.

---

## Running the Engine

Clone the repository:

```bash
git clone https://github.com/viktor924/gangtheft.git
```

Navigate to the project directory:

```bash
cd gangtheft
```

Run the engine:

```bash
python run.py
```

---

## Roadmap

The project is actively evolving. Planned development areas include:

- [ ] Runtime object manipulation.
- [ ] Advanced object management.
- [ ] Collision detection.
- [ ] Expanded physics simulation.
- [ ] 3D model loading.
- [ ] Material system.
- [ ] Texture loading and UV mapping.
- [ ] Lighting and shadow systems.
- [ ] Building and vegetation placement.
- [ ] Roads and vehicle systems.
- [ ] Advanced world streaming.
- [ ] Rendering optimizations.
- [ ] Audio engine.
- [ ] User interface system.
- [ ] Expanded open-world capabilities.

Visual texturing and detailed materials are intentionally postponed until the foundational engine systems are more mature.

---

## Development Philosophy

Viktor3D is being developed from the ground up rather than built on top of an existing game engine.

The project focuses on understanding and implementing the fundamental technologies behind a 3D game engine:

- Graphics programming.
- Rendering architecture.
- Mathematics.
- Memory and resource management.
- Procedural generation.
- World streaming.
- Physics.
- Object-oriented engine architecture.

The goal is to build a fully custom, modular 3D engine that can eventually support complex and detailed open-world environments.

---

## License

The project is currently under active development.

A license will be specified separately.

---

**Viktor3D Engine — Built from the ground up.**
