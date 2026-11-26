
import ctypes
from ctypes import wintypes


# ==========================================
# WINDOWS API
# ==========================================

user32 = ctypes.windll.user32

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG)
    ]


# Windows API definitions

user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = ctypes.c_short

user32.GetCursorPos.argtypes = [
    ctypes.POINTER(POINT)
]
user32.GetCursorPos.restype = wintypes.BOOL

user32.ScreenToClient.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(POINT)
]
user32.ScreenToClient.restype = wintypes.BOOL

user32.ClientToScreen.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(POINT)
]
user32.ClientToScreen.restype = wintypes.BOOL

user32.SetCursorPos.argtypes = [
    ctypes.c_int,
    ctypes.c_int
]
user32.SetCursorPos.restype = wintypes.BOOL

user32.ShowCursor.argtypes = [wintypes.BOOL]
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

        # Mouse position
        self.mouse_x = 0
        self.mouse_y = 0

        # Mouse movement
        self.mouse_delta_x = 0
        self.mouse_delta_y = 0

        # Mouse lock
        self.mouse_locked = False

        self._previous_mouse_x = None
        self._previous_mouse_y = None

        self._initialized = False

        print("[Input] Input system initialized.")

    # ======================================
    # UPDATE
    # ======================================

    def update(self, hwnd):

        # Save previous states
        self._previous_keys = self._current_keys.copy()
        self._previous_mouse = self._current_mouse.copy()

        self._current_keys.clear()
        self._current_mouse.clear()

        # ==================================
        # KEYBOARD POLLING
        # ==================================

        for key in range(1, 256):

            state = user32.GetAsyncKeyState(key)

            if state & 0x8000:
                self._current_keys.add(key)

        # ==================================
        # MOUSE BUTTONS
        # ==================================

        for button in (
            self.MOUSE_LEFT,
            self.MOUSE_RIGHT,
            self.MOUSE_MIDDLE
        ):

            state = user32.GetAsyncKeyState(button)

            if state & 0x8000:
                self._current_mouse.add(button)

        # ==================================
        # MOUSE POSITION
        # ==================================

        point = POINT()

        if user32.GetCursorPos(ctypes.byref(point)):

            if user32.ScreenToClient(
                hwnd,
                ctypes.byref(point)
            ):

                self.mouse_x = point.x
                self.mouse_y = point.y

        # ==================================
        # MOUSE MOVEMENT
        # ==================================

        if self.mouse_locked:

            center_x = self._center_x
            center_y = self._center_y

            self.mouse_delta_x = self.mouse_x - center_x
            self.mouse_delta_y = self.mouse_y - center_y

        else:

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

        return (
            self.mouse_delta_x,
            self.mouse_delta_y
        )

    # ======================================
    # CURSOR VISIBILITY
    # ======================================

    def set_cursor_visible(self, visible):

        while True:

            result = user32.ShowCursor(bool(visible))

            if visible and result >= 0:
                break

            if not visible and result < 0:
                break

    # ======================================
    # MOUSE LOCK
    # ======================================

    def set_mouse_locked(
        self,
        hwnd,
        locked,
        width,
        height
    ):

        self.mouse_locked = bool(locked)

        self._center_x = width // 2
        self._center_y = height // 2

        self.mouse_delta_x = 0
        self.mouse_delta_y = 0

        self._previous_mouse_x = None
        self._previous_mouse_y = None

        if self.mouse_locked:

            self.set_cursor_visible(False)

            self.set_mouse_position(
                hwnd,
                self._center_x,
                self._center_y
            )

        else:

            self.set_cursor_visible(True)

    # ======================================
    # MOUSE POSITION SET
    # ======================================

    def set_mouse_position(self, hwnd, x, y):

        point = POINT(int(x), int(y))

        if not user32.ClientToScreen(
            hwnd,
            ctypes.byref(point)
        ):
            return

        user32.SetCursorPos(
            point.x,
            point.y
        )

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

        self._initialized = False
