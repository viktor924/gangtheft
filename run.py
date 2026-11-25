
from engine.core.engine import Engine


def main():
    engine = Engine(
        title="Viktor3D Engine",
        width=1280,
        height=720,
        target_fps=60
    )

    engine.set_clear_color(
        0.08,
        0.12,
        0.20,
        1.0
    )

    engine.run()


if __name__ == "__main__":
    main()