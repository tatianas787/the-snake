from random import randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр экрана:
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Мапер разрешенных направлений:
DIRECTION_CHANGE_DICT = {
    (UP, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN
}

# Цветовое оформление фона и объектов:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Если появляется этот цвет, значит не был передан body_color у объекта.
BASE_COLOR = (255, 0, 255)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=CENTER_POSITION, body_color=BASE_COLOR):
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position, color=None, border=1):
        """Отрисовываем одну ячейку на игровом поле."""
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, color, rect, border)

    def draw(self):
        """Метод отрисовки объекта. Переопределяется в дочерних классах."""
        raise NotImplementedError(
            f"Класс '{self.__class__.__name__}'"
            f"должен реализовать метод draw()"
        )


class Apple(GameObject):
    """Класс яблока."""

    def __init__(
        self,
        occupied_positions=None,
        position=None,
        body_color=APPLE_COLOR
    ):
        """Инициализация яблока."""
        super().__init__(position, body_color)

        positions_for_check = (occupied_positions if occupied_positions
                               else [CENTER_POSITION])

        if position is None:
            self.randomize_position(positions_for_check)

    def randomize_position(self, occupied_positions):
        """Генерирование случайной позиции для яблока."""
        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            self.position = (x, y)
            # Проверяем, что позиция не занята.
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовка яблока."""
        self.draw_cell(self.position, color=APPLE_COLOR)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        """Инициализация змейки."""
        super().__init__(CENTER_POSITION, SNAKE_COLOR)
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.last = None

    def move(self):
        """Движение змейки."""
        self.update_direction()

        head_x, head_y = self.get_head_position()

        # Вычисляем новую позицию головы с учетом прохода сквозь границы.
        direction_x, direction_y = self.direction
        new_head_x = (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH
        new_head_y = (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_head_x, new_head_y)

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def reset(self):
        """Сбрасывание змейки в начальное состояние."""
        self.length = 1
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.last = None

    def draw(self):
        """Отрисовка змейки."""
        # Отрисовка головы змейки.
        super().draw_cell(self.get_head_position(), BORDER_COLOR, 1)

        # Затирание последнего сегмента.
        if self.last:
            super().draw_cell(self.last, BOARD_BACKGROUND_COLOR, 0)

    def get_head_position(self):
        """Возвращение позиции головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновление текущего направления движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def handle_keys(game_object):
    """Обрабатка нажатий клавиш."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            new_direction = DIRECTION_CHANGE_DICT.get(
                (game_object.direction, event.key),
                game_object.direction
            )
            game_object.next_direction = new_direction


def main():
    """Основная функция игры."""
    pg.init()

    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    while True:
        handle_keys(snake)
        snake.move()
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied_positions=snake.positions)

        elif snake.get_head_position() in snake.positions[1:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.randomize_position(occupied_positions=snake.positions)

        apple.draw()
        snake.draw()

        pg.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
