
import ctypes
from ctypes import wintypes


# ============================================================
# OPENGL CONSTANTS
# ============================================================

GL_COLOR_BUFFER_BIT = 0x00004000
GL_DEPTH_BUFFER_BIT = 0x00000100

GL_DEPTH_TEST = 0x0B71
GL_LEQUAL = 0x0203
GL_TRIANGLES = 0x0004
GL_UNSIGNED_INT = 0x1405


# ============================================================
# OPENGL DATA TYPES
# ============================================================

GLenum = ctypes.c_uint
GLbitfield = ctypes.c_uint
GLint = ctypes.c_int
GLsizei = ctypes.c_int
GLfloat = ctypes.c_float


# ============================================================
# WINDOWS API
# ============================================================

user32 = ctypes.WinDLL("user32", use_last_error=True)

user32.GetClientRect.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(wintypes.RECT)
]

user32.GetClientRect.restype = wintypes.BOOL


# ============================================================
# RENDERER
# ============================================================

class Renderer:

    def __init__(self, gpu_context):

        self.gpu = gpu_context

        self.initialized = False

        self.width = 0
        self.height = 0

        self.clear_color = (0.08, 0.10, 0.15, 1.0)

        self.frame_count = 0

        # FPS tracking
        self.fps = 0
        self._fps_frames = 0
        self._fps_time = 0.0

        self._initialize()

    # --------------------------------------------------------
    # INITIALIZE RENDERER
    # --------------------------------------------------------

    def _initialize(self):

        self.gpu.make_current()

        self._load_functions()

        self._update_viewport()

        # Enable depth testing
        self.glEnable(GL_DEPTH_TEST)

        self.glDepthFunc(GL_LEQUAL)

        # Initial background color
        self._apply_clear_color()

        self.initialized = True

        print("[Renderer] Initialized successfully.")

    # --------------------------------------------------------
    # LOAD OPENGL FUNCTIONS
    # --------------------------------------------------------

    def _load_function(self, name, restype, argtypes):

        address = self.gpu.get_proc_address(name)

        if not address:
            raise RuntimeError(
                f"OpenGL function loading failed: {name}"
            )

        function_type = ctypes.WINFUNCTYPE(
            restype,
            *argtypes
        )

        return function_type(address)

    def _load_functions(self):

        self.glViewport = self._load_function(
            "glViewport",
            None,
            [GLint, GLint, GLsizei, GLsizei]
        )

        self.glClearColor = self._load_function(
            "glClearColor",
            None,
            [GLfloat, GLfloat, GLfloat, GLfloat]
        )

        self.glClear = self._load_function(
            "glClear",
            None,
            [GLbitfield]
        )

        self.glEnable = self._load_function(
            "glEnable",
            None,
            [GLenum]
        )

        self.glDepthFunc = self._load_function(
            "glDepthFunc",
            None,
            [GLenum]
        )

        self.glDrawElements = self._load_function(
            "glDrawElements",
            None,
            [GLenum, GLsizei, GLenum, ctypes.c_void_p]
        )

    # --------------------------------------------------------
    # VIEWPORT
    # --------------------------------------------------------

    def _update_viewport(self):

        rect = wintypes.RECT()

        success = user32.GetClientRect(
            self.gpu.hwnd,
            ctypes.byref(rect)
        )

        if not success:
            raise RuntimeError(
                "Failed to get window dimensions."
            )

        width = rect.right - rect.left
        height = rect.bottom - rect.top

        self.width = max(1, width)
        self.height = max(1, height)

        self.glViewport(
            0,
            0,
            self.width,
            self.height
        )

    # --------------------------------------------------------
    # BACKGROUND COLOR
    # --------------------------------------------------------

    def set_clear_color(self, red, green, blue, alpha=1.0):

        values = (red, green, blue, alpha)

        if any(value < 0.0 or value > 1.0 for value in values):
            raise ValueError(
                "Color values must be between 0.0 and 1.0."
            )

        self.clear_color = values

        self._apply_clear_color()

    def _apply_clear_color(self):

        self.glClearColor(
            *self.clear_color
        )

    # --------------------------------------------------------
    # BEGIN FRAME
    # --------------------------------------------------------

    def begin_frame(self):

        if not self.initialized:
            raise RuntimeError(
                "Renderer is not initialized."
            )

        self.gpu.make_current()

        self._update_viewport()

        self.glClear(
            GL_COLOR_BUFFER_BIT |
            GL_DEPTH_BUFFER_BIT
        )

    # --------------------------------------------------------
    # DRAW MESH
    # --------------------------------------------------------

    def draw_mesh(self, mesh, shader):

        if not self.initialized:
            raise RuntimeError(
                "Renderer is not initialized."
            )

        if not mesh.initialized:
            raise RuntimeError(
                "Mesh is not initialized."
            )

        if not shader.initialized:
            raise RuntimeError(
                "Shader is not initialized."
            )

        shader.use()

        mesh.bind()

        self.glDrawElements(
            GL_TRIANGLES,
            mesh.index_count,
            GL_UNSIGNED_INT,
            None
        )

        mesh.unbind()

    # --------------------------------------------------------
    # END FRAME
    # --------------------------------------------------------

    def end_frame(self):

        if not self.initialized:
            return

        self.gpu.swap_buffers()

        self.frame_count += 1

        self._update_fps()

    # --------------------------------------------------------
    # FPS COUNTER
    # --------------------------------------------------------

    def _update_fps(self):

        import time

        current_time = time.perf_counter()

        self._fps_frames += 1

        elapsed = current_time - self._fps_time

        if elapsed >= 1.0:

            self.fps = int(
                self._fps_frames / elapsed
            )

            self._fps_frames = 0
            self._fps_time = current_time

    # --------------------------------------------------------
    # RENDERER INFORMATION
    # --------------------------------------------------------

    def get_information(self):

        return {
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "frames": self.frame_count,
            "clear_color": self.clear_color,
            "initialized": self.initialized
        }

    # --------------------------------------------------------
    # SHUTDOWN
    # --------------------------------------------------------

    def close(self):

        self.initialized = False

        print("[Renderer] Shutdown complete.")