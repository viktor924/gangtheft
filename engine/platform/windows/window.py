
import ctypes
import os

from ctypes import wintypes


# ============================================================
# WINDOWS API
# ============================================================

if os.name != "nt":
    raise OSError("Viktor3D jelenleg csak Windows rendszeren fut.")


user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


# ============================================================
# WINDOWS CONSTANTS
# ============================================================

CS_HREDRAW = 0x0002
CS_VREDRAW = 0x0001
CS_OWNDC = 0x0020

WS_OVERLAPPEDWINDOW = 0x00CF0000
WS_VISIBLE = 0x10000000

CW_USEDEFAULT = 0x80000000

WM_DESTROY = 0x0002
WM_CLOSE = 0x0010
WM_QUIT = 0x0012
WM_SIZE = 0x0005

SW_SHOW = 5


# ============================================================
# WINDOWS STRUCTURES
# ============================================================

class WNDCLASSW(ctypes.Structure):
    pass


WNDPROC = ctypes.WINFUNCTYPE(
    ctypes.c_longlong,
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM
)


WNDCLASSW._fields_ = [
    ("style", wintypes.UINT),
    ("lpfnWndProc", WNDPROC),
    ("cbClsExtra", ctypes.c_int),
    ("cbWndExtra", ctypes.c_int),
    ("hInstance", wintypes.HINSTANCE),
    ("hIcon", wintypes.HICON),
    ("hCursor", wintypes.HANDLE),
    ("hbrBackground", wintypes.HANDLE),
    ("lpszMenuName", wintypes.LPCWSTR),
    ("lpszClassName", wintypes.LPCWSTR),
]


# ============================================================
# WINDOWS API FUNCTION DEFINITIONS
# ============================================================

kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE

user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
user32.RegisterClassW.restype = wintypes.ATOM

user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.HINSTANCE,
    wintypes.LPVOID,
]

user32.CreateWindowExW.restype = wintypes.HWND

user32.ShowWindow.argtypes = [
    wintypes.HWND,
    ctypes.c_int
]

user32.UpdateWindow.argtypes = [
    wintypes.HWND
]

user32.DestroyWindow.argtypes = [
    wintypes.HWND
]

user32.DefWindowProcW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM
]

user32.DefWindowProcW.restype = ctypes.c_longlong

user32.PeekMessageW.argtypes = [
    ctypes.POINTER(wintypes.MSG),
    wintypes.HWND,
    wintypes.UINT,
    wintypes.UINT,
    wintypes.UINT
]

user32.PeekMessageW.restype = wintypes.BOOL

user32.TranslateMessage.argtypes = [
    ctypes.POINTER(wintypes.MSG)
]

user32.DispatchMessageW.argtypes = [
    ctypes.POINTER(wintypes.MSG)
]

user32.PostQuitMessage.argtypes = [
    ctypes.c_int
]


# ============================================================
# WINDOW CLASS
# ============================================================

class Window:

    def __init__(
        self,
        title="Viktor3D Engine",
        width=1280,
        height=720
    ):

        self.title = title
        self.width = width
        self.height = height

        self.running = False
        self.hwnd = None

        self.hinstance = kernel32.GetModuleHandleW(None)

        self.class_name = "Viktor3DWindowClass"

        self._wndproc = WNDPROC(self._window_proc)

        self._register_window_class()
        self._create_window()

    # --------------------------------------------------------
    # REGISTER WINDOW CLASS
    # --------------------------------------------------------

    def _register_window_class(self):

        window_class = WNDCLASSW()

        window_class.style = CS_HREDRAW | CS_VREDRAW | CS_OWNDC
        window_class.lpfnWndProc = self._wndproc
        window_class.cbClsExtra = 0
        window_class.cbWndExtra = 0
        window_class.hInstance = self.hinstance
        window_class.hIcon = None
        window_class.hCursor = None
        window_class.hbrBackground = None
        window_class.lpszMenuName = None
        window_class.lpszClassName = self.class_name

        atom = user32.RegisterClassW(
            ctypes.byref(window_class)
        )

        if not atom:
            error = ctypes.get_last_error()

            # ERROR_CLASS_ALREADY_EXISTS
            if error != 1410:
                raise ctypes.WinError(error)

    # --------------------------------------------------------
    # CREATE WINDOW
    # --------------------------------------------------------

    def _create_window(self):

        self.hwnd = user32.CreateWindowExW(
            0,
            self.class_name,
            self.title,
            WS_OVERLAPPEDWINDOW | WS_VISIBLE,
            CW_USEDEFAULT,
            CW_USEDEFAULT,
            self.width,
            self.height,
            None,
            None,
            self.hinstance,
            None
        )

        if not self.hwnd:
            raise ctypes.WinError(ctypes.get_last_error())

        user32.ShowWindow(self.hwnd, SW_SHOW)
        user32.UpdateWindow(self.hwnd)

        self.running = True

    # --------------------------------------------------------
    # WINDOW MESSAGE HANDLER
    # --------------------------------------------------------

    def _window_proc(
        self,
        hwnd,
        message,
        wparam,
        lparam
    ):

        if message == WM_CLOSE:

            self.running = False
            return 0

        elif message == WM_DESTROY:

            self.running = False
            user32.PostQuitMessage(0)
            return 0

        return user32.DefWindowProcW(
            hwnd,
            message,
            wparam,
            lparam
        )

    # --------------------------------------------------------
    # PROCESS WINDOWS EVENTS
    # --------------------------------------------------------

    def poll_events(self):

        message = wintypes.MSG()

        while user32.PeekMessageW(
            ctypes.byref(message),
            None,
            0,
            0,
            1
        ):

            if message.message == WM_QUIT:
                self.running = False
                return

            user32.TranslateMessage(
                ctypes.byref(message)
            )

            user32.DispatchMessageW(
                ctypes.byref(message)
            )

    # --------------------------------------------------------
    # CLOSE WINDOW
    # --------------------------------------------------------

    def close(self):
        if self.hwnd:

            user32.DestroyWindow(self.hwnd)
            self.hwnd = None

        self.running = False

    # --------------------------------------------------------
    # WINDOW STATUS
    # --------------------------------------------------------

    def is_open(self):

        return self.running