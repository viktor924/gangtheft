
import ctypes


# ==========================================
# OPENGL CONSTANTS
# ==========================================

GL_ARRAY_BUFFER = 0x8892
GL_ELEMENT_ARRAY_BUFFER = 0x8893

GL_STATIC_DRAW = 0x88E4

GL_FLOAT = 0x1406
GL_UNSIGNED_INT = 0x1405

GL_TRIANGLES = 0x0004


# ==========================================
# MESH
# ==========================================

class Mesh:

    def __init__(self, gpu_context, vertices, indices, colors=None):

        self.gpu = gpu_context

        self.vao = 0
        self.vbo = 0
        self.ebo = 0

        self.vertex_count = 0
        self.index_count = 0

        self.vertex_data = None
        self.index_data = None

        self.color_data = None
        self.color_vbo = 0

        self.initialized = False

        self._validate_data(vertices, indices, colors)

        self._load_functions()

        self._create_mesh(vertices, indices, colors)

    # ======================================
    # VALIDATION
    # ======================================

    def _validate_data(self, vertices, indices, colors=None):
        if not vertices:
            raise ValueError("Mesh vertices cannot be empty.")

        if not indices:
            raise ValueError("Mesh indices cannot be empty.")

        if len(vertices) % 3 != 0:
            raise ValueError(
                "Vertices must contain XYZ coordinates."
            )

        vertex_count = len(vertices) // 3

        for index in indices:

            if not isinstance(index, int):
                raise TypeError("Mesh indices must be integers.")

            if index < 0 or index >= vertex_count:
                raise ValueError(
                    f"Invalid mesh index: {index}"
                )

        if colors is not None:

            if len(colors) != vertex_count * 3:
                raise ValueError(
                    "Colors must contain RGB values for every vertex."
                )

    # ======================================
    # LOAD OPENGL FUNCTIONS
    # ======================================

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

        self.glGenVertexArrays = self._load_function(
            "glGenVertexArrays",
            None,
            [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
        )

        self.glBindVertexArray = self._load_function(
            "glBindVertexArray",
            None,
            [ctypes.c_uint]
        )

        self.glGenBuffers = self._load_function(
            "glGenBuffers",
            None,
            [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
        )

        self.glBindBuffer = self._load_function(
            "glBindBuffer",
            None,
            [ctypes.c_uint, ctypes.c_uint]
        )

        self.glBufferData = self._load_function(
            "glBufferData",
            None,
            [
                ctypes.c_uint,
                ctypes.c_size_t,
                ctypes.c_void_p,
                ctypes.c_uint
            ]
        )

        self.glEnableVertexAttribArray = self._load_function(
            "glEnableVertexAttribArray",
            None,
            [ctypes.c_uint]
        )

        self.glVertexAttribPointer = self._load_function(
            "glVertexAttribPointer",
            None,
            [
                ctypes.c_uint,
                ctypes.c_int,
                ctypes.c_uint,
                ctypes.c_ubyte,
                ctypes.c_int,
                ctypes.c_void_p
            ]
        )

        self.glDeleteVertexArrays = self._load_function(
            "glDeleteVertexArrays",
            None,
            [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
        )

        self.glDeleteBuffers = self._load_function(
            "glDeleteBuffers",
            None,
            [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
        )

    # ======================================
    # CREATE MESH
    # ======================================

    def _create_mesh(self, vertices, indices, colors=None):

        self.gpu.make_current()

        vertex_data = (ctypes.c_float * len(vertices))(
            *vertices
        )

        index_data = (ctypes.c_uint * len(indices))(
            *indices
        )

        self.vertex_data = vertex_data
        self.index_data = index_data
        color_data = None

        if colors is not None:
            color_data = (ctypes.c_float * len(colors))(
                *colors
            )

        self.color_data = color_data

        try:
            # Create VAO
            vao = ctypes.c_uint()
            self.glGenVertexArrays(1, ctypes.byref(vao))
            self.vao = vao.value

            self.glBindVertexArray(self.vao)

            # Vertex color attribute
            if color_data is not None:

                color_vbo = ctypes.c_uint()
                self.glGenBuffers(1, ctypes.byref(color_vbo))
                self.color_vbo = color_vbo.value

                self.glBindBuffer(
                    GL_ARRAY_BUFFER,
                    self.color_vbo
                )

                self.glBufferData(
                    GL_ARRAY_BUFFER,
                    ctypes.sizeof(color_data),
                    ctypes.cast(color_data, ctypes.c_void_p),
                    GL_STATIC_DRAW
                )

                self.glEnableVertexAttribArray(1)

                self.glVertexAttribPointer(
                    1,
                    3,
                    GL_FLOAT,
                    0,
                    3 * ctypes.sizeof(ctypes.c_float),
                    None
                )

            # Create VBO
            vbo = ctypes.c_uint()
            self.glGenBuffers(1, ctypes.byref(vbo))
            self.vbo = vbo.value

            self.glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

            self.glBufferData(
                GL_ARRAY_BUFFER,
                ctypes.sizeof(vertex_data),
                ctypes.cast(vertex_data, ctypes.c_void_p),
                GL_STATIC_DRAW
            )

            # Create EBO
            ebo = ctypes.c_uint()
            self.glGenBuffers(1, ctypes.byref(ebo))
            self.ebo = ebo.value

            self.glBindBuffer(
                GL_ELEMENT_ARRAY_BUFFER,
                self.ebo
            )

            self.glBufferData(
                GL_ELEMENT_ARRAY_BUFFER,
                ctypes.sizeof(index_data),
                ctypes.cast(index_data, ctypes.c_void_p),
                GL_STATIC_DRAW
            )

            # Vertex position attribute
            self.glEnableVertexAttribArray(0)

            self.glVertexAttribPointer(
                0,
                3,
                GL_FLOAT,
                0,
                3 * ctypes.sizeof(ctypes.c_float),
                None
            )

            # Unbind VAO
            self.glBindVertexArray(0)

            self.vertex_count = len(vertices) // 3
            self.index_count = len(indices)

            self.initialized = True

            print("[Mesh] Mesh uploaded to GPU successfully.")

        except Exception:
            self.close()
            raise

    # ======================================
    # BIND / UNBIND
    # ======================================

    def bind(self):

        if not self.initialized:
            raise RuntimeError("Mesh is not initialized.")

        self.gpu.make_current()
        self.glBindVertexArray(self.vao)

    def unbind(self):

        self.glBindVertexArray(0)

    # ======================================
    # SHUTDOWN
    # ======================================

    def close(self):

        if not self.gpu:
            return

        self.gpu.make_current()

        if self.vao:
            vao = ctypes.c_uint(self.vao)
            self.glDeleteVertexArrays(
                1,
                ctypes.byref(vao)
            )
            self.vao = 0

        if self.vbo:
            vbo = ctypes.c_uint(self.vbo)
            self.glDeleteBuffers(
                1,
                ctypes.byref(vbo)
            )
            self.vbo = 0

        if self.ebo:
            ebo = ctypes.c_uint(self.ebo)
            self.glDeleteBuffers(
                1,
                ctypes.byref(ebo)
            )
            self.ebo = 0

        if self.color_vbo:
            color_vbo = ctypes.c_uint(self.color_vbo)
            self.glDeleteBuffers(
                1,
                ctypes.byref(color_vbo)
            )
            self.color_vbo = 0

        self.initialized = False

        print("[Mesh] Mesh resources released.")