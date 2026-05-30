import random

import spritePro as s
from .config import FOOD_COUNT, FOOD_SIZE, FOOD_COLORS, WORLD_WIDTH, WORLD_HEIGHT


class FoodManager:
    def __init__(self, scene: s.Scene):
        self.scene = scene
        self.foods: list[s.Sprite] = []
        self._spawn_initial()

    def _spawn_initial(self) -> None:
        for _ in range(FOOD_COUNT):
            self.spawn()

    def spawn_at(self, pos: tuple[int, int]) -> s.Sprite:
        color = random.choice(FOOD_COLORS)
        food = s.Sprite("", (FOOD_SIZE * 2, FOOD_SIZE * 2), pos, scene=self.scene)
        food.set_circle_shape(radius=FOOD_SIZE, color=color)
        food.set_sorting_order(1)
        food._ctype = "food"
        self.foods.append(food)
        return food

    def spawn(self) -> s.Sprite:
        margin = FOOD_SIZE
        x = random.randint(margin, WORLD_WIDTH - margin)
        y = random.randint(margin, WORLD_HEIGHT - margin)
        color = random.choice(FOOD_COLORS)
        return self.spawn_at((x, y))

    def check_eating(self, head_sprite: s.Sprite) -> list[s.Sprite]:
        eaten: list[s.Sprite] = []
        to_remove: list[s.Sprite] = []

        for food in self.foods:
            if not food.active:
                to_remove.append(food)
                continue
            if head_sprite.rect.colliderect(food.rect):
                eaten.append(food)
                to_remove.append(food)

        for food in to_remove:
            if food in self.foods:
                self.foods.remove(food)
            if food.active:
                s.disable_sprite(food)

        return eaten

    def maintain_count(self) -> None:
        while len(self.foods) < FOOD_COUNT:
            self.spawn()

    def clear(self) -> None:
        for food in self.foods:
            if food.active:
                s.disable_sprite(food)
        self.foods.clear()
