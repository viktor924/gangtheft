
import ctypes
import time


# ==========================================
# WINDOWS API
# ==========================================

user32 = ctypes.windll.user32


class POINT(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long)
    ]


user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = ctypes.c_short

user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
user32.GetCursorPos.restype = ctypes.c_bool

user32.ScreenToClient.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(POINT)
]
user32.ScreenToClient.restype = ctypes.c_bool

user32.ClientToScreen.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(POINT)
]
user32.ClientToScreen.restype = ctypes.c_bool

user32.ShowCursor.argtypes = [ctypes.c_bool]
user32.ShowCursor.restype = ctypes.c_int


# ==========================================
# INPUT SYSTEM
# ==========================================

class Input:

    # Keyboard
    KEY_SPACE = 0x20
    KEY_ESCAPE = 0x1B
    KEY_ENTER = 0x0D
    KEY_SHIFT = 0x10
    KEY_CTRL = 0x11
    KEY_ALT = 0x12
    KEY_TAB = 0x09

    KEY_W = 0x57
    KEY_A = 0x41
    KEY_S = 0x53
    KEY_D = 0x44

    KEY_UP = 0x26
    KEY_DOWN = 0x28
    KEY_LEFT = 0x25
    KEY_RIGHT = 0x27

    # Mouse
    MOUSE_LEFT = 0x01
    MOUSE_RIGHT = 0x02
    MOUSE_MIDDLE = 0x04

    def __init__(self):

        self._current_keys = set()
        self._previous_keys = set()

        self._current_mouse = set()
        self._previous_mouse = set()

        self.mouse_x = 0
        self.mouse_y = 0

        self.mouse_delta_x = 0
        self.mouse_delta_y = 0

        self._previous_mouse_x = None
        self._previous_mouse_y = None

        self._initialized = False

        print("[Input] Input system initialized.")

    # ======================================
    # UPDATE
    # ======================================

    def update(self, hwnd):

        self._previous_keys = self._current_keys.copy()
        self._previous_mouse = self._current_mouse.copy()

        self._current_keys.clear()
        self._current_mouse.clear()

        # Keyboard polling
        for key in range(1, 256):

            state = user32.GetAsyncKeyState(key)

            if state & 0x8000:
                self._current_keys.add(key)

        # Mouse buttons
        for button in (
            self.MOUSE_LEFT,
            self.MOUSE_RIGHT,
            self.MOUSE_MIDDLE
        ):

            state = user32.GetAsyncKeyState(button)

            if state & 0x8000:
                self._current_mouse.add(button)

        # Mouse position
        point = POINT()

        if user32.GetCursorPos(ctypes.byref(point)):

            user32.ScreenToClient(hwnd, ctypes.byref(point))

            self.mouse_x = point.x
            self.mouse_y = point.y

        # Mouse movement
        if self._previous_mouse_x is not None:

            self.mouse_delta_x = (
                self.mouse_x - self._previous_mouse_x
            )

            self.mouse_delta_y = (
                self.mouse_y - self._previous_mouse_y
            )

        else:

            self.mouse_delta_x = 0
            self.mouse_delta_y = 0

        self._previous_mouse_x = self.mouse_x
        self._previous_mouse_y = self.mouse_y

        self._initialized = True

    # ======================================
    # KEYBOARD
    # ======================================

    def is_key_down(self, key):

        return key in self._current_keys

    def is_key_pressed(self, key):

        return (
            key in self._current_keys
            and key not in self._previous_keys
        )

    def is_key_released(self, key):

        return (
            key in self._previous_keys
            and key not in self._current_keys
        )

    # ======================================
    # MOUSE BUTTONS
    # ======================================

    def is_mouse_down(self, button):

        return button in self._current_mouse

    def is_mouse_pressed(self, button):

        return (
            button in self._current_mouse
            and button not in self._previous_mouse
        )

    def is_mouse_released(self, button):

        return (
            button in self._previous_mouse
            and button not in self._current_mouse
        )

    # ======================================
    # MOUSE POSITION
    # ======================================

    def get_mouse_position(self):

        return self.mouse_x, self.mouse_y

    def get_mouse_delta(self):

        return self.mouse_delta_x, self.mouse_delta_y

    # ======================================
    # CURSOR
    # ======================================

    def set_cursor_visible(self, visible):

        if visible:

            while user32.ShowCursor(True) < 0:
                pass

        else:

            while user32.ShowCursor(False) >= 0:
                pass

    def set_mouse_position(self, hwnd, x, y):

        point = POINT(x, y)

        user32.ClientToScreen(hwnd, ctypes.byref(point))

        user32.SetCursorPos(point.x, point.y)

        self._previous_mouse_x = None
        self._previous_mouse_y = None

    # ======================================
    # RESET
    # ======================================

    def reset(self):

        self._current_keys.clear()
        self._previous_keys.clear()

        self._current_mouse.clear()
        self._previous_mouse.clear()

        self.mouse_delta_x = 0
        self.mouse_delta_y = 0

        self._previous_mouse_x = None
        self._previous_mouse_y = None