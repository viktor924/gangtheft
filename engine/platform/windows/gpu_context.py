
import ctypes
from ctypes import wintypes


# ============================================================
# WINDOWS GRAPHICS API
# ============================================================

gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
opengl32 = ctypes.WinDLL("opengl32", use_last_error=True)
user32 = ctypes.WinDLL("user32", use_last_error=True)


HDC = ctypes.c_void_p
HGLRC = ctypes.c_void_p


# ============================================================
# PIXEL FORMAT CONSTANTS
# ============================================================

PFD_TYPE_RGBA = 0
PFD_MAIN_PLANE = 0

PFD_DOUBLEBUFFER = 0x00000001
PFD_DRAW_TO_WINDOW = 0x00000004
PFD_SUPPORT_OPENGL = 0x00000020


# ============================================================
# OPENGL CONSTANTS
# ============================================================

GL_VENDOR = 0x1F00
GL_RENDERER = 0x1F01
GL_VERSION = 0x1F02

WGL_CONTEXT_MAJOR_VERSION_ARB = 0x2091
WGL_CONTEXT_MINOR_VERSION_ARB = 0x2092
WGL_CONTEXT_PROFILE_MASK_ARB = 0x9126

WGL_CONTEXT_CORE_PROFILE_BIT_ARB = 0x00000001


# ============================================================
# PIXEL FORMAT STRUCTURE
# ============================================================

class PIXELFORMATDESCRIPTOR(ctypes.Structure):

    _fields_ = [
        ("nSize", wintypes.WORD),
        ("nVersion", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("iPixelType", wintypes.BYTE),
        ("cColorBits", wintypes.BYTE),
        ("cRedBits", wintypes.BYTE),
        ("cRedShift", wintypes.BYTE),
        ("cGreenBits", wintypes.BYTE),
        ("cGreenShift", wintypes.BYTE),
        ("cBlueBits", wintypes.BYTE),
        ("cBlueShift", wintypes.BYTE),
        ("cAlphaBits", wintypes.BYTE),
        ("cAlphaShift", wintypes.BYTE),
        ("cAccumBits", wintypes.BYTE),
        ("cAccumRedBits", wintypes.BYTE),
        ("cAccumGreenBits", wintypes.BYTE),
        ("cAccumBlueBits", wintypes.BYTE),
        ("cAccumAlphaBits", wintypes.BYTE),
        ("cDepthBits", wintypes.BYTE),
        ("cStencilBits", wintypes.BYTE),
        ("cAuxBuffers", wintypes.BYTE),
        ("iLayerType", ctypes.c_byte),
        ("bReserved", wintypes.BYTE),
        ("dwLayerMask", wintypes.DWORD),
        ("dwVisibleMask", wintypes.DWORD),
        ("dwDamageMask", wintypes.DWORD),
    ]


# ============================================================
# OPENGL FUNCTION TYPES
# ============================================================

WGLCREATECONTEXTATTRIBSARB = ctypes.WINFUNCTYPE(
    HGLRC,
    HDC,
    HGLRC,
    ctypes.POINTER(ctypes.c_int)
)


# ============================================================
# WINDOWS API DEFINITIONS
# ============================================================

user32.GetDC.argtypes = [wintypes.HWND]
user32.GetDC.restype = HDC

user32.ReleaseDC.argtypes = [wintypes.HWND, HDC]
user32.ReleaseDC.restype = ctypes.c_int

gdi32.ChoosePixelFormat.argtypes = [
    HDC,
    ctypes.POINTER(PIXELFORMATDESCRIPTOR)
]
gdi32.ChoosePixelFormat.restype = ctypes.c_int

gdi32.SetPixelFormat.argtypes = [
    HDC,
    ctypes.c_int,
    ctypes.POINTER(PIXELFORMATDESCRIPTOR)
]
gdi32.SetPixelFormat.restype = wintypes.BOOL

gdi32.SwapBuffers.argtypes = [HDC]
gdi32.SwapBuffers.restype = wintypes.BOOL

opengl32.wglCreateContext.argtypes = [HDC]
opengl32.wglCreateContext.restype = HGLRC

opengl32.wglDeleteContext.argtypes = [HGLRC]
opengl32.wglDeleteContext.restype = wintypes.BOOL

opengl32.wglMakeCurrent.argtypes = [HDC, HGLRC]
opengl32.wglMakeCurrent.restype = wintypes.BOOL

opengl32.wglGetProcAddress.argtypes = [ctypes.c_char_p]
opengl32.wglGetProcAddress.restype = ctypes.c_void_p

opengl32.glGetString.argtypes = [wintypes.UINT]
opengl32.glGetString.restype = ctypes.c_char_p

# ============================================================
# GPU CONTEXT
# ============================================================

class GPUContext:

    def __init__(self, window, major=3, minor=3):

        self.window = window
        self.hwnd = window.hwnd

        self.hdc = None
        self.hglrc = None

        self.major = major
        self.minor = minor

        self.initialized = False

        self.vendor = ""
        self.renderer = ""
        self.version = ""

        self._initialize()

    # --------------------------------------------------------
    # INITIALIZATION
    # --------------------------------------------------------

    def _initialize(self):

        self._get_device_context()
        self._set_pixel_format()

        # Temporary legacy context.
        legacy_context = opengl32.wglCreateContext(self.hdc)

        if not legacy_context:
            raise RuntimeError("Nem sikerült létrehozni az alap OpenGL contextet.")

        if not opengl32.wglMakeCurrent(self.hdc, legacy_context):
            opengl32.wglDeleteContext(legacy_context)
            raise RuntimeError("Nem sikerült aktiválni az alap OpenGL contextet.")

        try:
            self._create_modern_context(legacy_context)

        except Exception:
            opengl32.wglMakeCurrent(None, None)
            opengl32.wglDeleteContext(legacy_context)
            raise

        opengl32.wglMakeCurrent(None, None)
        opengl32.wglDeleteContext(legacy_context)

        if not opengl32.wglMakeCurrent(self.hdc, self.hglrc):
            raise RuntimeError("Nem sikerült aktiválni a modern OpenGL contextet.")

        self._read_gpu_information()

        self.initialized = True

    # --------------------------------------------------------
    # DEVICE CONTEXT
    # --------------------------------------------------------

    def _get_device_context(self):

        self.hdc = user32.GetDC(self.hwnd)

        if not self.hdc:
            raise RuntimeError("Nem sikerült lekérni a Windows Device Contextet.")

    # --------------------------------------------------------
    # PIXEL FORMAT
    # --------------------------------------------------------

    def _set_pixel_format(self):

        pfd = PIXELFORMATDESCRIPTOR()

        pfd.nSize = ctypes.sizeof(PIXELFORMATDESCRIPTOR)
        pfd.nVersion = 1

        pfd.dwFlags = (
            PFD_DRAW_TO_WINDOW |
            PFD_SUPPORT_OPENGL |
            PFD_DOUBLEBUFFER
        )

        pfd.iPixelType = PFD_TYPE_RGBA
        pfd.cColorBits = 32
        pfd.cDepthBits = 24
        pfd.cStencilBits = 8
        pfd.iLayerType = PFD_MAIN_PLANE

        pixel_format = gdi32.ChoosePixelFormat(
            self.hdc,
            ctypes.byref(pfd)
        )

        if not pixel_format:
            raise RuntimeError("Nem található megfelelő pixel format.")

        if not gdi32.SetPixelFormat(
            self.hdc,
            pixel_format,
            ctypes.byref(pfd)
        ):
            raise RuntimeError("Nem sikerült beállítani a pixel formatot.")

    # --------------------------------------------------------
    # CREATE MODERN OPENGL CONTEXT
    # --------------------------------------------------------

    def _create_modern_context(self, legacy_context):

        address = opengl32.wglGetProcAddress(
            b"wglCreateContextAttribsARB"
        )

        if not self._valid_address(address):
            raise RuntimeError(
                "A videókártya illesztőprogramja nem támogatja "
                "a WGL modern context létrehozását."
            )

        create_context = WGLCREATECONTEXTATTRIBSARB(address)

        attributes = (ctypes.c_int * 7)(
            WGL_CONTEXT_MAJOR_VERSION_ARB,
            self.major,
            WGL_CONTEXT_MINOR_VERSION_ARB,
            self.minor,
            WGL_CONTEXT_PROFILE_MASK_ARB,
            WGL_CONTEXT_CORE_PROFILE_BIT_ARB,
            0
        )

        self.hglrc = create_context(
            self.hdc,
            None,
            attributes
        )

        if not self.hglrc:
            raise RuntimeError(
                f"Nem sikerült létrehozni az OpenGL "
                f"{self.major}.{self.minor} Core Contextet."
            )

    # --------------------------------------------------------
    # OPENGL FUNCTION ADDRESS VALIDATION
    # --------------------------------------------------------

    @staticmethod
    def _valid_address(address):

        if not address:
            return False

        value = ctypes.cast(
            address,
            ctypes.c_void_p
        ).value

        return value not in (1, 2, 3, 0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF)

    # --------------------------------------------------------
    # LOAD OPENGL FUNCTION
    # --------------------------------------------------------

    def get_proc_address(self, function_name):

        if isinstance(function_name, str):
            function_name = function_name.encode("ascii")

        address = opengl32.wglGetProcAddress(function_name)

        if self._valid_address(address):
            return address

        try:
            return ctypes.cast(
                getattr(opengl32, function_name.decode("ascii")),
                ctypes.c_void_p
            ).value

        except AttributeError:
            raise RuntimeError(
                f"OpenGL funkció nem található: {function_name.decode('ascii')}"
            )

    # --------------------------------------------------------
    # GPU INFORMATION
    # --------------------------------------------------------

    def _read_gpu_information(self):

        self.vendor = opengl32.glGetString(GL_VENDOR).decode(
            "utf-8", errors="replace"
        )

        self.renderer = opengl32.glGetString(GL_RENDERER).decode(
            "utf-8", errors="replace"
        )

        self.version = opengl32.glGetString(GL_VERSION).decode(
            "utf-8", errors="replace"
        )

    # --------------------------------------------------------
    # ACTIVATE CONTEXT
    # --------------------------------------------------------

    def make_current(self):

        if not opengl32.wglMakeCurrent(self.hdc, self.hglrc):
            raise RuntimeError("GPU context aktiválási hiba.")

    # --------------------------------------------------------
    # PRESENT FRAME
    # --------------------------------------------------------

    def swap_buffers(self):

        if not gdi32.SwapBuffers(self.hdc):
            raise RuntimeError("Nem sikerült megjeleníteni a GPU képkockát.")

    # --------------------------------------------------------
    # INFORMATION
    # --------------------------------------------------------

    def print_information(self):

        print("========== VIKTOR3D GPU ==========")
        print(f"Vendor:   {self.vendor}")
        print(f"Renderer: {self.renderer}")
        print(f"Version:  {self.version}")
        print("==================================")

    # --------------------------------------------------------
    # SHUTDOWN
    # --------------------------------------------------------

    def close(self):

        if self.hglrc:

            opengl32.wglMakeCurrent(None, None)
            opengl32.wglDeleteContext(self.hglrc)

            self.hglrc = None

        if self.hdc:

            user32.ReleaseDC(self.hwnd, self.hdc)
            self.hdc = None

        self.initialized = False