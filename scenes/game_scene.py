import pygame
import spritePro as s
from game.config import (
    WORLD_WIDTH, WORLD_HEIGHT, BOT_COUNT,
    BOT_RESPAWN_DELAY, HEAD_SIZE, FOOD_SIZE,
)
from game.snake import Snake
from game.bot import BotSnake
from game.food import FoodManager
from game.world import World
from ui.hud import HUD


def _circle_collide(
    a: tuple[int, int], b: tuple[int, int],
    ra: int, rb: int,
) -> bool:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy < (ra + rb) * (ra + rb)


class GameScene(s.Scene):
    def __init__(self):
        super().__init__()
        self._init_game()

    def _init_game(self) -> None:
        self.score = 0
        self.game_over = False
        self._respawn_queue = 0
        self._respawn_timer = 0.0

        self.world = World(self)
        start = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.snake = Snake(start, self)

        self.bots: list[BotSnake] = []
        self._spawn_bots()

        self.food = FoodManager(self)
        self.hud = HUD(self)

        s.set_camera_follow(self.snake.head, (0, 0))
        s.set_camera_zoom(0.6)

    def on_exit(self) -> None:
        s.clear_camera_follow()

    def update(self, dt: float) -> None:
        if self.game_over:
            if s.input.was_pressed(pygame.K_r):
                self._restart()
            return

        self.snake.update(dt)
        for bot in self.bots:
            bot.update(dt, self.food.foods)

        self.food.maintain_count()
        self._check_collisions()

        entries = [("Player", self.snake)]
        for i, bot in enumerate(self.bots):
            if bot.alive:
                entries.append((f"Bot {i+1}", bot))
        self.hud.update_leaderboard(entries)

        self._update_respawn(dt)

    def _check_collisions(self) -> None:
        head = self.snake.head

        for food in list(self.food.foods):
            if food.active and _circle_collide(head.rect.center, food.rect.center, HEAD_SIZE // 2, FOOD_SIZE):
                self._player_eat(food)

        for bot in self.bots:
            if not bot.alive:
                continue
            for seg in bot.segments:
                if seg.active and head.rect.colliderect(seg.rect):
                    self._trigger_game_over()
                    return

        for wall in self.world.walls:
            if head.rect.colliderect(wall.rect):
                self._trigger_game_over()
                return

        for bot in self.bots:
            if not bot.alive:
                continue
            for food in list(self.food.foods):
                if food.active and _circle_collide(bot.head.rect.center, food.rect.center, HEAD_SIZE // 2, FOOD_SIZE):
                    self._bot_eat(bot.head, food)
                    break
            for seg in self.snake.segments:
                if seg.active and bot.head.rect.colliderect(seg.rect):
                    self._bot_killed(bot.head)
                    break

    def _player_eat(self, food_sprite: s.Sprite) -> None:
        if self.game_over:
            return
        if food_sprite.active:
            s.disable_sprite(food_sprite)
        if food_sprite in self.food.foods:
            self.food.foods.remove(food_sprite)
        self.score += 1
        self.snake.grow()
        self.hud.update_score(self.score)
        self.hud.update_length(len(self.snake.segments))
        self.food.maintain_count()

    def _bot_eat(self, bot_head: s.Sprite, food_sprite: s.Sprite) -> None:
        if food_sprite.active:
            s.disable_sprite(food_sprite)
        if food_sprite in self.food.foods:
            self.food.foods.remove(food_sprite)
        for bot in self.bots:
            if bot.head is bot_head and bot.alive:
                bot.grow()
                self.food.maintain_count()
                break

    def _bot_killed(self, bot_head: s.Sprite) -> None:
        for bot in self.bots:
            if bot.head is bot_head and bot.alive:
                bot.alive = False
                self._kill_bot(bot)
                return

    def _spawn_bots(self) -> None:
        import random as _r
        for _ in range(BOT_COUNT):
            x = _r.randint(200, WORLD_WIDTH - 200)
            y = _r.randint(200, WORLD_HEIGHT - 200)
            self.bots.append(BotSnake((x, y), self))

    def _update_respawn(self, dt: float) -> None:
        if self._respawn_queue <= 0:
            return
        self._respawn_timer += dt
        if self._respawn_timer >= BOT_RESPAWN_DELAY:
            self._respawn_timer = 0.0
            self._respawn_queue -= 1
            import random as _r
            x = _r.randint(200, WORLD_WIDTH - 200)
            y = _r.randint(200, WORLD_HEIGHT - 200)
            self.bots.append(BotSnake((x, y), self))

    def _kill_bot(self, bot: BotSnake) -> None:
        segments = [bot.head] + bot.segments
        for seg in segments:
            self.food.spawn_at(seg.rect.center)
            if seg.active:
                s.disable_sprite(seg)
        bot.segments.clear()
        bot.trail.clear()
        bot.alive = False
        if bot in self.bots:
            self.bots.remove(bot)
        self._respawn_queue += 1
        self.score += 5
        self.hud.update_score(self.score)

    def _trigger_game_over(self) -> None:
        self.game_over = True
        self.snake.die()
        for bot in self.bots:
            for seg in [bot.head] + bot.segments:
                if seg.active:
                    s.disable_sprite(seg)
            bot.segments.clear()
            bot.trail.clear()
            bot.alive = False
        self.bots.clear()
        self.hud.show_game_over(self.score)

    def _restart(self) -> None:
        for sprite in list(s.get_game().all_sprites):
            if getattr(sprite, "scene", None) is self and sprite.active:
                s.disable_sprite(sprite)
        self._init_game()
