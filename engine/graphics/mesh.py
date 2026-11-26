import ctypes
import math

GL_ARRAY_BUFFER = 0x8892
GL_ELEMENT_ARRAY_BUFFER = 0x8893
GL_STATIC_DRAW = 0x88E4
GL_FLOAT = 0x1406
GL_UNSIGNED_INT = 0x1405
GL_TRIANGLES = 0x0004


class Mesh:

    def __init__(self, gpu_context, vertices, indices, colors=None, normals=None):
        self.gpu = gpu_context
        self.vao = 0
        self.vbo = 0
        self.ebo = 0
        self.color_vbo = 0
        self.normal_vbo = 0

        self.vertex_count = 0
        self.index_count = 0
        self.initialized = False

        if normals is None:
            normals = self._compute_normals(vertices, indices)

        self._validate_data(vertices, indices, colors, normals)
        self._load_functions()
        self._create_mesh(vertices, indices, colors, normals)

    @staticmethod
    def _compute_normals(vertices, indices):
        v_count = len(vertices) // 3
        normals = [0.0] * (v_count * 3)

        for i in range(0, len(indices), 3):
            i0, i1, i2 = indices[i], indices[i + 1], indices[i + 2]
            ax, ay, az = vertices[i0 * 3], vertices[i0 * 3 + 1], vertices[i0 * 3 + 2]
            bx, by, bz = vertices[i1 * 3], vertices[i1 * 3 + 1], vertices[i1 * 3 + 2]
            cx, cy, cz = vertices[i2 * 3], vertices[i2 * 3 + 1], vertices[i2 * 3 + 2]

            ux, uy, uz = bx - ax, by - ay, bz - az
            vx, vy, vz = cx - ax, cy - ay, cz - az

            nx = uy * vz - uz * vy
            ny = uz * vx - ux * vz
            nz = ux * vy - uy * vx

            for idx in (i0, i1, i2):
                normals[idx * 3] += nx
                normals[idx * 3 + 1] += ny
                normals[idx * 3 + 2] += nz

        for i in range(v_count):
            nx, ny, nz = normals[i * 3], normals[i * 3 + 1], normals[i * 3 + 2]
            length = math.sqrt(nx * nx + ny * ny + nz * nz)
            if length > 1e-6:
                normals[i * 3] /= length
                normals[i * 3 + 1] /= length
                normals[i * 3 + 2] /= length
            else:
                normals[i * 3 + 1] = 1.0

        return normals

    def _validate_data(self, vertices, indices, colors=None, normals=None):
        if not vertices or not indices:
            raise ValueError("Mesh vertices and indices cannot be empty.")
        if len(vertices) % 3 != 0:
            raise ValueError("Vertices must contain XYZ coordinates.")
        vertex_count = len(vertices) // 3
        if colors is not None and len(colors) != vertex_count * 3:
            raise ValueError("Colors must match vertex count.")
        if normals is not None and len(normals) != vertex_count * 3:
            raise ValueError("Normals must match vertex count.")

    def _load_function(self, name, restype, argtypes):
        address = self.gpu.get_proc_address(name)
        if not address:
            raise RuntimeError(f"OpenGL function loading failed: {name}")
        return ctypes.WINFUNCTYPE(restype, *argtypes)(address)

    def _load_functions(self):
        self.glGenVertexArrays = self._load_function("glGenVertexArrays", None, [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)])
        self.glBindVertexArray = self._load_function("glBindVertexArray", None, [ctypes.c_uint])
        self.glGenBuffers = self._load_function("glGenBuffers", None, [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)])
        self.glBindBuffer = self._load_function("glBindBuffer", None, [ctypes.c_uint, ctypes.c_uint])
        self.glBufferData = self._load_function("glBufferData", None, [ctypes.c_uint, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_uint])
        self.glEnableVertexAttribArray = self._load_function("glEnableVertexAttribArray", None, [ctypes.c_uint])
        self.glVertexAttribPointer = self._load_function("glVertexAttribPointer", None, [ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_ubyte, ctypes.c_int, ctypes.c_void_p])
        self.glDeleteVertexArrays = self._load_function("glDeleteVertexArrays", None, [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)])
        self.glDeleteBuffers = self._load_function("glDeleteBuffers", None, [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)])

    def _upload_vbo(self, location, data_list):
        c_data = (ctypes.c_float * len(data_list))(*data_list)
        vbo = ctypes.c_uint()
        self.glGenBuffers(1, ctypes.byref(vbo))
        self.glBindBuffer(GL_ARRAY_BUFFER, vbo.value)
        self.glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(c_data), ctypes.cast(c_data, ctypes.c_void_p), GL_STATIC_DRAW)
        self.glEnableVertexAttribArray(location)
        self.glVertexAttribPointer(location, 3, GL_FLOAT, 0, 3 * ctypes.sizeof(ctypes.c_float), None)
        return vbo.value, c_data

    def _create_mesh(self, vertices, indices, colors=None, normals=None):
        self.gpu.make_current()
        self.index_data = (ctypes.c_uint * len(indices))(*indices)

        try:
            vao = ctypes.c_uint()
            self.glGenVertexArrays(1, ctypes.byref(vao))
            self.vao = vao.value
            self.glBindVertexArray(self.vao)

            self.vbo, self.vertex_data = self._upload_vbo(0, vertices)

            if colors is None:
                colors = [1.0] * len(vertices)
            self.color_vbo, self.color_data = self._upload_vbo(1, colors)

            if normals is not None:
                self.normal_vbo, self.normal_data = self._upload_vbo(2, normals)

            ebo = ctypes.c_uint()
            self.glGenBuffers(1, ctypes.byref(ebo))
            self.ebo = ebo.value
            self.glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            self.glBufferData(GL_ELEMENT_ARRAY_BUFFER, ctypes.sizeof(self.index_data), ctypes.cast(self.index_data, ctypes.c_void_p), GL_STATIC_DRAW)

            self.glBindVertexArray(0)
            self.vertex_count = len(vertices) // 3
            self.index_count = len(indices)
            self.initialized = True
        except Exception:
            self.close()
            raise

    def bind(self):
        if not self.initialized:
            raise RuntimeError("Mesh is not initialized.")
        self.gpu.make_current()
        self.glBindVertexArray(self.vao)

    def unbind(self):
        self.glBindVertexArray(0)

    def close(self):
        if not self.gpu:
            return
        self.gpu.make_current()
        if self.vao:
            vao = ctypes.c_uint(self.vao)
            self.glDeleteVertexArrays(1, ctypes.byref(vao))
            self.vao = 0
        for buf in (self.vbo, self.ebo, self.color_vbo, self.normal_vbo):
            if buf:
                b = ctypes.c_uint(buf)
                self.glDeleteBuffers(1, ctypes.byref(b))
        self.vbo = self.ebo = self.color_vbo = self.normal_vbo = 0
        self.initialized = False