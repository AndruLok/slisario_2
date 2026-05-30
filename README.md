# Слизарио

**Slither.io**-подобная мультиплеерная игра на Python с использованием фреймворка **SpritePro** (поверх pygame).

---

## План разработки

### 1. Архитектура проекта

```
slisario_2/
├── main.py              # точка входа
├── README.md
├── requirements.txt
├── assets/              # спрайты, текстуры, звуки
│   ├── snake/
│   ├── food/
│   ├── map/
│   └── ui/
├── server.py            # выделенный сервер (опционально)
├── game/
│   ├── __init__.py
│   ├── config.py        # константы (скорости, размеры, цвета)
│   ├── snake.py         # класс Snake (голова + сегменты)
│   ├── food.py          # класс Food, спавн еды
│   ├── world.py         # игровой мир, границы, логика
│   └── camera.py        # настройки камеры (follow)
├── multiplayer/
│   ├── __init__.py
│   ├── messages.py      # типы сетевых сообщений
│   ├── handler.py       # обработка входящих событий
│   └── sync.py          # синхронизация состояний
├── scenes/
│   ├── __init__.py
│   ├── menu.py          # главное меню
│   ├── lobby.py         # лобби (список игроков)
│   ├── game_scene.py    # основная игровая сцена
│   └── game_over.py     # экран завершения
└── ui/
    ├── __init__.py
    ├── hud.py           # счёт, длина, топ игроков
    └── leaderboard.py   # таблица лидеров
```

---

### 2. Этапы реализации

#### Этап 1: Одиночная игра (локал)

**Цель:** работающий геймплей змейки в одном окне.

- **Snake (`game/snake.py`)**
  - Голова — `s.Sprite` с физическим телом `DYNAMIC`.
  - Движение по направлению мыши (поворот головы в сторону курсора).
  - Сегменты тела — массив спрайтов, движутся по цепочке за головой.
  - При столкновении с едой — увеличение длины и скорости.

- **Food (`game/food.py`)**
  - Спавн случайных точек на карте.
  - `s.Sprite` кружок с коллизией `CIRCLE`.
  - При поедании — деспавн + спавн новой.

- **World (`game/world.py`)**
  - Прямоугольное поле с границами.
  - Коллизия головы с границами = смерть.
  - Коллизия головы с телом (своим или чужим) = смерть.

- **GameScene (`scenes/game_scene.py`)**
  - Инициализация `PhysicsWorld`.
  - `update(dt)`: движение змеи, обработка коллизий, спавн еды.
  - Камера следует за головой (`set_camera_follow`).
  - HUD (длина змеи).

**SpritePro API:** `Sprite`, `PhysicsWorld`, `PhysicsBody`, `PhysicsConfig`, `BodyType.DYNAMIC`, `set_camera_follow`, `zoom_camera`, `Scene`, `s.input`.

---

#### Этап 2: Мультиплеер (локальный)

**Цель:** два игрока на одном сервере.

- **Сервер (`server.py` или встроенный host-mode)**
  - `NetServer` на `0.0.0.0:5050`.
  - Релеит JSON-сообщения между клиентами.

- **Клиент**
  - `NetClient` подключается к серверу.
  - `MultiplayerContext` — роль, ID, список игроков.

- **Сетевой протокол (`multiplayer/messages.py`)**
  - `pos` — координаты головы + направление сегментов.
  - `eat` — съедена еда (id еды, id игрока).
  - `death` — игрок умер.
  - `join/leave` — подключение/отключение.

- **Синхронизация (`multiplayer/sync.py`)**
  - Каждый кадр отправляем `pos` (с троттлингом `send_every`).
  - При получении `pos` — интерполируем позицию чужой змеи.
  - Еда спавнится одинаково на всех клиентах (общий seed).

- **Лобби (`scenes/lobby.py`)**
  - `MultiplayerLobbyScene` из `readyScenes/`.
  - Поле ввода имени, кнопка Ready, список игроков.

**SpritePro API:** `NetServer`, `NetClient`, `MultiplayerContext`, `send_every`, `poll`, `readyScenes.multiplayer_lobby`, `ChatScene`.

---

#### Этап 3: Полировка и контент

- **Меню (`scenes/menu.py`)**
  - Кнопки: "Играть" (ввод IP), "Создать сервер", "Выйти".
  - Настройки (скорость мыши, громкость).
  - Использовать `s.Button`, `s.TextSprite`.

- **Game Over (`scenes/game_over.py`)**
  - Показывает длину, место, кнопку "Заново".

- **Leaderboard (`ui/leaderboard.py`)**
  - Таблица в углу экрана (топ-10 по длине).
  - Обновляется в реальном времени.

- **Визуал**
  - Сегменты тела — плавные градиенты, случайный цвет игрока.
  - Еда — разноцветные кружки, анимация `tween_punch_scale`.
  - Фон — сетка (`GridRenderer`) или текстура.
  - Частицы при поедании еды (`ParticleEmitter`, `template_sparks`).

- **Звук**
  - Фоновая музыка через `AudioManager`.
  - SFX: поедание, смерть, подключение игрока.

**SpritePro API:** `Button`, `TextSprite`, `GridRenderer`, `ParticleEmitter`, `template_sparks`, `AudioManager`, `tween_punch_scale`.

---

### 3. Сетевой протокол

Формат сообщений — JSON строки через `\n`:

```json
// Клиент → Сервер
{"event": "player_join", "data": {"name": "Игрок1"}}
{"event": "pos",        "data": {"x": 100.5, "y": 200.3, "angle": 45.0, "segments": [...]}}
{"event": "eat",        "data": {"food_id": 7}}
{"event": "ready",      "data": {}}

// Сервер → Все
{"event": "player_list", "data": {"players": [{"id": 0, "name": "Хост"}, ...]}}
{"event": "food_spawn",  "data": {"food": [{"id": 1, "x": 50, "y": 100}, ...]}}
{"event": "player_died", "data": {"id": 2, "killer_id": 0, "length": 15}}
{"event": "game_start",  "data": {"seed": 1337, "player_count": 4}}
```

---

### 4. Физика и движение

- Змея движется за счёт ручного обновления позиции (`move` или прямая установка `set_position`), а не pymunk-физики (для плавного управления).
- Pymunk используется только для:
  - Коллизии голова-еда (триггер).
  - Коллизии голова-граница (смерть).
  - Опционально — толчки между змеями.
- Голова: `Sprite + PhysicsBody(shape=CIRCLE, body_type=DYNAMIC)`.
- Сегменты: `Sprite + PhysicsBody(shape=CIRCLE, body_type=KINEMATIC)` следуют за головой через цепочку (каждый сегмент держит дистанцию до предыдущего).

---

### 5. Используемые возможности SpritePro

| Компонент          | Назначение                                           |
|-------------------|------------------------------------------------------|
| `s.Sprite`        | Голова, сегменты, еда, UI-элементы                   |
| `s.Scene`         | Базовый класс для всех сцен                          |
| `s.SceneManager`  | Переключение между Menu → Lobby → Game → GameOver    |
| `s.PhysicsWorld`  | Мир pymunk, коллизии                                 |
| `s.PhysicsBody`   | Физическое тело для спрайта                          |
| `s.NetServer`     | TCP-сервер (ретрансляция)                            |
| `s.NetClient`     | TCP-клиент                                           |
| `s.MultiplayerContext` | Контекст мультиплеера (ID, роль, игроки)        |
| `s.send_every`    | Троттлинг отправки позиций                          |
| `s.Camera`        | Follow за головой игрока                             |
| `s.Button`        | Кнопки меню                                          |
| `s.TextSprite`    | Текст (HUD, никнеймы)                                |
| `s.ParticleEmitter` | Эффекты при поедании                              |
| `s.AudioManager`  | Музыка и звуки                                       |
| `s.Tween`         | Анимации (еда пульсирует, сегменты плавно двигаются) |
| `s.input`         | Ввод с клавиатуры/мыши                               |

---

### 6. Запуск

```bash
# Установка SpritePro
pip install spritepro

# Одиночная игра
python main.py

# Мультиплеер (сервер + первый игрок)
python main.py --host 0.0.0.0 --port 5050

# Мультиплеер (клиент)
python main.py --host IP_СЕРВЕРА --port 5050

# Выделенный сервер (без графики)
python server.py --host 0.0.0.0 --port 5050
```
