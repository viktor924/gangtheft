
import ctypes


# ==========================================
# OPENGL CONSTANTS
# ==========================================

GL_VERTEX_SHADER = 0x8B31
GL_FRAGMENT_SHADER = 0x8B30

GL_COMPILE_STATUS = 0x8B81
GL_LINK_STATUS = 0x8B82

GL_INFO_LOG_LENGTH = 0x8B84

GL_FALSE = 0


# ==========================================
# SHADER
# ==========================================

class Shader:

    def __init__(self, gpu_context, vertex_source, fragment_source):

        self.gpu = gpu_context

        self.program = 0
        self.initialized = False

        self._load_functions()

        vertex_shader = self._compile_shader(
            GL_VERTEX_SHADER,
            vertex_source
        )

        fragment_shader = self._compile_shader(
            GL_FRAGMENT_SHADER,
            fragment_source
        )

        try:
            self.program = self.glCreateProgram()

            self.glAttachShader(self.program, vertex_shader)
            self.glAttachShader(self.program, fragment_shader)

            self.glLinkProgram(self.program)

            status = ctypes.c_int()

            self.glGetProgramiv(
                self.program,
                GL_LINK_STATUS,
                ctypes.byref(status)
            )

            if not status.value:
                raise RuntimeError(
                    "Shader linking failed:\n" +
                    self._get_program_log(self.program)
                )

            self.initialized = True

            print("[Shader] Shader program created successfully.")

        except Exception:
            if self.program:
                self.glDeleteProgram(self.program)
                self.program = 0
            raise

        finally:
            self.glDeleteShader(vertex_shader)
            self.glDeleteShader(fragment_shader)

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

        self.glCreateShader = self._load_function(
            "glCreateShader",
            ctypes.c_uint,
            [ctypes.c_uint]
        )

        self.glShaderSource = self._load_function(
            "glShaderSource",
            None,
            [
                ctypes.c_uint,
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_char_p),
                ctypes.POINTER(ctypes.c_int)
            ]
        )

        self.glCompileShader = self._load_function(
            "glCompileShader",
            None,
            [ctypes.c_uint]
        )

        self.glGetShaderiv = self._load_function(
            "glGetShaderiv",
            None,
            [
                ctypes.c_uint,
                ctypes.c_uint,
                ctypes.POINTER(ctypes.c_int)
            ]
        )

        self.glGetShaderInfoLog = self._load_function(
            "glGetShaderInfoLog",
            None,
            [
                ctypes.c_uint,
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_int),
                ctypes.c_char_p
            ]
        )

        self.glCreateProgram = self._load_function(
            "glCreateProgram",
            ctypes.c_uint,
            []
        )

        self.glAttachShader = self._load_function(
            "glAttachShader",
            None,
            [ctypes.c_uint, ctypes.c_uint]
        )

        self.glLinkProgram = self._load_function(
            "glLinkProgram",
            None,
            [ctypes.c_uint]
        )

        self.glGetProgramiv = self._load_function(
            "glGetProgramiv",
            None,
            [
                ctypes.c_uint,
                ctypes.c_uint,
                ctypes.POINTER(ctypes.c_int)
            ]
        )

        self.glGetProgramInfoLog = self._load_function(
            "glGetProgramInfoLog",
            None,
            [
                ctypes.c_uint,
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_int),
                ctypes.c_char_p
            ]
        )

        self.glDeleteShader = self._load_function(
            "glDeleteShader",
            None,
            [ctypes.c_uint]
        )

        self.glDeleteProgram = self._load_function(
            "glDeleteProgram",
            None,
            [ctypes.c_uint]
        )

        self.glUseProgram = self._load_function(
            "glUseProgram",
            None,
            [ctypes.c_uint]
        )

        self.glGetUniformLocation = self._load_function(
            "glGetUniformLocation",
            ctypes.c_int,
            [ctypes.c_uint, ctypes.c_char_p]
        )

        self.glUniformMatrix4fv = self._load_function(
            "glUniformMatrix4fv",
            None,
            [
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_ubyte,
                ctypes.POINTER(ctypes.c_float)
            ]
        )

        self.glUniform4f = self._load_function(
            "glUniform4f",
            None,
            [
                ctypes.c_int,
                ctypes.c_float,
                ctypes.c_float,
                ctypes.c_float,
                ctypes.c_float
            ]
        )

    # ======================================
    # COMPILE SHADER
    # ======================================

    def _compile_shader(self, shader_type, source):

        shader = self.glCreateShader(shader_type)

        if not shader:
            raise RuntimeError("Failed to create shader.")

        source_bytes = source.encode("utf-8")
        source_pointer = ctypes.c_char_p(source_bytes)

        source_array = (ctypes.c_char_p * 1)(
            source_pointer
        )

        self.glShaderSource(
            shader,
            1,
            source_array,
            None
        )

        self.glCompileShader(shader)

        status = ctypes.c_int()

        self.glGetShaderiv(
            shader,
            GL_COMPILE_STATUS,
            ctypes.byref(status)
        )

        if not status.value:
            log = self._get_shader_log(shader)
            self.glDeleteShader(shader)

            raise RuntimeError(
                "Shader compilation failed:\n" + log
            )

        return shader

    # ======================================
    # ERROR LOGS
    # ======================================

    def _get_shader_log(self, shader):

        length = ctypes.c_int()

        self.glGetShaderiv(
            shader,
            GL_INFO_LOG_LENGTH,
            ctypes.byref(length)
        )

        if length.value <= 1:
            return "No shader information available."

        buffer = ctypes.create_string_buffer(length.value)

        self.glGetShaderInfoLog(
            shader,
            length.value,
            None,
            buffer
        )

        return buffer.value.decode("utf-8", errors="replace")

    def _get_program_log(self, program):

        length = ctypes.c_int()

        self.glGetProgramiv(
            program,
            GL_INFO_LOG_LENGTH,
            ctypes.byref(length)
        )

        if length.value <= 1:
            return "No program information available."

        buffer = ctypes.create_string_buffer(length.value)

        self.glGetProgramInfoLog(
            program,
            length.value,
            None,
            buffer
        )

        return buffer.value.decode("utf-8", errors="replace")

    # ======================================
    # USE SHADER
    # ======================================

    def use(self):

        if not self.initialized:
            raise RuntimeError("Shader is not initialized.")

        self.glUseProgram(self.program)

    # ======================================
    # UNIFORM VARIABLES
    # ======================================

    def get_uniform_location(self, name):

        location = self.glGetUniformLocation(
            self.program,
            name.encode("utf-8")
        )

        if location == -1:
            print(f"[Shader] Warning: Uniform not found: {name}")

        return location

    def set_matrix4(self, name, matrix):

        self.use()

        location = self.get_uniform_location(name)

        if location == -1:
            return

        values = (ctypes.c_float * 16)(*matrix.to_list())

        self.glUniformMatrix4fv(
            location,
            1,
            GL_FALSE,
            values
        )

    def set_vector4(self, name, x, y, z, w):

        self.use()

        location = self.get_uniform_location(name)

        if location == -1:
            return

        self.glUniform4f(
            location,
            x,
            y,
            z,
            w
        )

    # ======================================
    # SHUTDOWN
    # ======================================

    def close(self):

        if self.program:

            self.glUseProgram(0)
            self.glDeleteProgram(self.program)

            self.program = 0
            self.initialized = False

            print("[Shader] Shader destroyed.")