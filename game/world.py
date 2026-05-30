import spritePro as s
from .config import WORLD_WIDTH, WORLD_HEIGHT, FILL_COLOR


class World:
    def __init__(self, scene: s.Scene):
        self.scene = scene

        self.bg = s.Sprite(
            "", (WORLD_WIDTH, WORLD_HEIGHT), (WORLD_WIDTH // 2, WORLD_HEIGHT // 2),
            scene=scene,
        )
        self.bg.set_rect_shape(
            size=(WORLD_WIDTH, WORLD_HEIGHT),
            color=FILL_COLOR,
        )
        self.bg.set_sorting_order(0)

        border_color = (40, 40, 60)
        border_width = 20
        walls_data = [
            ((WORLD_WIDTH // 2, 10), (WORLD_WIDTH, border_width), "wall_top"),
            ((WORLD_WIDTH // 2, WORLD_HEIGHT - 10), (WORLD_WIDTH, border_width), "wall_bottom"),
            ((10, WORLD_HEIGHT // 2), (border_width, WORLD_HEIGHT), "wall_left"),
            ((WORLD_WIDTH - 10, WORLD_HEIGHT // 2), (border_width, WORLD_HEIGHT), "wall_right"),
        ]
        self.walls: list[s.Sprite] = []
        for pos, size, _ in walls_data:
            wall = s.Sprite("", size, pos, scene=scene)
            wall.set_rect_shape(size=size, color=border_color)
            wall.set_sorting_order(2)
            wall._ctype = "wall"
            self.walls.append(wall)
