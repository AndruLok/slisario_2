import spritePro as s


class HUD:
    def __init__(self, scene: s.Scene):
        self.score_label = s.TextSprite(
            "Score: 0",
            font_size=28,
            color=(200, 200, 200),
            pos=(20, 20),
            scene=scene,
        )
        self.score_label.set_position((20, 20), anchor="topleft")
        self.score_label.set_screen_space(True)
        self.score_label.set_sorting_order(100)

        self.length_label = s.TextSprite(
            "Length: 5",
            font_size=22,
            color=(160, 160, 160),
            pos=(20, 55),
            scene=scene,
        )
        self.length_label.set_position((20, 55), anchor="topleft")
        self.length_label.set_screen_space(True)
        self.length_label.set_sorting_order(100)

    def update_score(self, score: int) -> None:
        self.score_label.set_text(f"Score: {score}")

    def update_length(self, length: int) -> None:
        self.length_label.set_text(f"Length: {length}")

    def show_game_over(self, score: int) -> None:
        self.score_label.set_text(f"Game Over! Score: {score}")
        self.score_label.set_position((s.WH_C.x, s.WH_C.y - 20))
        self.score_label.set_sorting_order(100)

        self.length_label.set_screen_space(True)
        self.length_label.set_text("Press R to restart")
        self.length_label.set_position((s.WH_C.x, s.WH_C.y + 20))

    def clear(self) -> None:
        if self.score_label.active:
            s.disable_sprite(self.score_label)
        if self.length_label.active:
            s.disable_sprite(self.length_label)
