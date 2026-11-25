
import time as system_time


class Time:
    # Időadatok
    delta_time = 0.0
    unscaled_delta_time = 0.0

    elapsed_time = 0.0
    time_scale = 1.0

    # FPS adatok
    fps = 0
    frame_count = 0

    # Belső időmérők
    _last_frame_time = 0.0
    _start_time = 0.0
    _fps_timer = 0.0
    _fps_frame_count = 0

    _initialized = False

    @classmethod
    def initialize(cls):
        now = system_time.perf_counter()

        cls.delta_time = 0.0
        cls.unscaled_delta_time = 0.0

        cls.elapsed_time = 0.0
        cls.time_scale = 1.0

        cls.fps = 0
        cls.frame_count = 0

        cls._last_frame_time = now
        cls._start_time = now
        cls._fps_timer = now
        cls._fps_frame_count = 0

        cls._initialized = True

    @classmethod
    def update(cls):
        if not cls._initialized:
            cls.initialize()
            return

        now = system_time.perf_counter()

        raw_delta = now - cls._last_frame_time
        cls._last_frame_time = now

        # Védelem extrém hosszú képkocka ellen.
        raw_delta = max(0.0, min(raw_delta, 0.25))

        cls.unscaled_delta_time = raw_delta
        cls.delta_time = raw_delta * cls.time_scale

        cls.elapsed_time += cls.delta_time
        cls.frame_count += 1

        # FPS számítás.
        cls._fps_frame_count += 1

        fps_elapsed = now - cls._fps_timer

        if fps_elapsed >= 1.0:
            cls.fps = round(
                cls._fps_frame_count / fps_elapsed
            )

            cls._fps_frame_count = 0
            cls._fps_timer = now

    @classmethod
    def set_time_scale(cls, scale):
        cls.time_scale = max(0.0, float(scale))

    @classmethod
    def reset_time_scale(cls):
        cls.time_scale = 1.0

    @classmethod
    def get_elapsed_time(cls):
        return cls.elapsed_time

    @classmethod
    def get_unscaled_elapsed_time(cls):
        if not cls._initialized:
            return 0.0

        return system_time.perf_counter() - cls._start_time

    @classmethod
    def get_frame_count(cls):
        return cls.frame_count

    @classmethod
    def get_fps(cls):
        return cls.fps

    @classmethod
    def get_delta_time(cls):
        return cls.delta_time

    @classmethod
    def get_time_scale(cls):
        return cls.time_scale

    @classmethod
    def is_initialized(cls):
        return cls._initialized