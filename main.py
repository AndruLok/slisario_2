import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import spritePro as s
from game.config import WINDOW_SIZE, FPS, TITLE, FILL_COLOR
from scenes.game_scene import GameScene


def main() -> None:
    s.run(
        scene=GameScene,
        size=WINDOW_SIZE,
        fps=FPS,
        title=TITLE,
        fill_color=FILL_COLOR,
    )


if __name__ == "__main__":
    if True:
        s.run(
            scene=GameScene,
            size=WINDOW_SIZE,
            fps=FPS,
            title=TITLE,
            fill_color=FILL_COLOR,
            multiplayer=True,
            multiplayer_use_lobby=False,
        )
    else:
        main()
