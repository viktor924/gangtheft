
import time as system_time

from engine.core.time import Time


class GameLoop:
    def __init__(self, engine, target_fps=0):
        self.engine = engine
        self.target_fps = max(0, int(target_fps))
        self.running = False

    def set_target_fps(self, fps):
        self.target_fps = max(0, int(fps))

    def stop(self):
        self.running = False

    def run(self):
        if self.running:
            return

        self.running = True
        Time.initialize()

        print("Viktor3D Game Loop started!")

        try:
            while self.running and self.engine.window.is_open():
                frame_start = system_time.perf_counter()

                # 1. Windows események feldolgozása
                self.engine.window.poll_events()

                # Input frissítése minden képkockában
                self.engine.input.update(self.engine.window.hwnd)

                if not self.engine.window.is_open():
                    break

                # 2. Idő frissítése
                Time.update()

                # 3. Játéklogika frissítése
                self.engine.update(Time.delta_time)

                # 4. Renderelés
                self.engine.renderer.begin_frame()
                self.engine.render()
                self.engine.renderer.end_frame()

                # 5. FPS limit
                if self.target_fps > 0:
                    frame_duration = (
                        system_time.perf_counter() - frame_start
                    )

                    target_duration = 1.0 / self.target_fps
                    remaining_time = target_duration - frame_duration

                    if remaining_time > 0:
                        system_time.sleep(remaining_time)

        finally:
            self.running = False
            print("Viktor3D Game Loop stopped!")