from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр поля:
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
ALL_DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Скорость движения змейки:
SPEED = 15

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    DEFAULT_COLOR = (255, 255, 255)  # Цвет по умолчанию - белый.

    def __init__(
            self,
            body_color: tuple[int, int, int] = DEFAULT_COLOR
    ) -> None:
        """Инициализирует игровой объект в центре поля."""
        self.position = SCREEN_CENTER
        self.body_color = body_color

    def draw_square(
            self,
            color: tuple[int, int, int],
            border_color: tuple[int, int, int],
            position: tuple[int, int]
    ) -> None:
        """Рисует 1 квадрат."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, border_color, rect, 1)

    def get_polygon_cords(
            self,
            cords: list[tuple[int, int]],
            position: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """Рассчитывает координаты для отрисовки фигуры нестандартной формы."""
        new_cords = []
        x_now, y_now = position
        for cord in cords:
            x, y = cord
            new_cords.append((x + x_now, y + y_now))
        return new_cords

    def get_line_cords(
            self,
            cords: list[tuple[int, int]],
            position: tuple[int, int]
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        """Рассчитывает координаты для отрисовки линии."""
        x_now, y_now = position
        x_start, y_start = cords[0]
        x_end, y_end = cords[1]
        return (
            (x_now + x_start, y_now + y_start),
            (x_now + x_end, y_now + y_end)
        )

    def draw(self) -> None:
        """Отрисовывает игровые объекты (реализация в дочерних классах)."""


class Apple(GameObject):
    """Класс для игрового объекта 'Яблоко'.

    'Яблоко' спавнится на случайных координатах поля,
    является целью для игрового объекта 'Змейка'.
    """

    APPLE_COLOR = (235, 78, 61)  # Цвет яблока - красный.
    BORDER_COLOR = (214, 64, 47)  # Цвет границы ячейки - темно-красный.
    STEM_COLOR = (56, 48, 31)  # Цвет хвостика яблока - коричневый.
    LEAF_COLOR = (47, 117, 54)  # Цвет листика яблока - зеленый.
    APPLE_CORDS = [
        (4, 6),  # Верх, лево, скос.
        (6, 4),  # Верх, лево, купол.
        (8, 4),
        (9, 4),  # Верх, центр.
        (11, 6),  # Верх, право, купол.
        (12, 4),
        (14, 4),  # Верх, право, купол.
        (16, 6),  # Верх, право, скос.
        (17, 8),
        (17, 14),  # Право, бок.
        (15, 17),  # Низ, право, скос.
        (12, 18),
        (10, 18),  # Низ, центр.
        (8, 18),  # Низ, лево, скос.
        (5, 17),
        (3, 14),  # Лево, бок.
        (3, 8)
    ]
    STEM_CORDS = [(10, 6), (11, 1)]
    LEAF_CORDS = [
        (11, 3),  # Лево.
        (13, 1),  # Верх.
        (16, 1),  # Верх, право.
        (16, 4),  # Низ, право.
        (13, 4)  # Низ, лево.
    ]
    HIGHLIGHT_CORDS = [(6, 6), (4, 8)]

    def __init__(
            self,
            snake_positions: list[tuple[int, int]] | None = None,
            body_color: tuple[int, int, int] = APPLE_COLOR
    ) -> None:
        """Инициализирует экземпляр игрового объекта 'Яблоко'
        и создает случайные стартовые координаты.
        """
        super().__init__(body_color)

        # snake_positions=None и [] для pytest
        self.randomize_position(snake_positions or [])

    def randomize_position(
            self, snake_positions: list[tuple[int, int]]
    ) -> None:
        """Определяет новые координаты 'Яблока' случайным образом."""
        while True:
            # Отнимаем 1, так как нумерация клеток идет от 0 до 31 и
            # от 0 до 23, при 32(x) и 24(y) клетках, на которые поделено поле.
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            self.position = (x, y)

            if self.position not in snake_positions:
                break

    def draw(self) -> None:
        """Отрисовывает 'Яблоко' на игровом поле."""
        # Рисуем тело яблока.
        body_cords = self.get_polygon_cords(self.APPLE_CORDS, self.position)
        pg.draw.polygon(screen, self.APPLE_COLOR, body_cords)
        pg.draw.polygon(screen, self.BORDER_COLOR, body_cords, 1)

        # Рисуем веточку.
        stem_start, stem_end = self.get_line_cords(
            self.STEM_CORDS, self.position
        )
        pg.draw.line(screen, self.STEM_COLOR, stem_start, stem_end, 2)

        # Рисуем листик.
        new_leaf_cords = self.get_polygon_cords(self.LEAF_CORDS, self.position)
        pg.draw.polygon(screen, self.LEAF_COLOR, new_leaf_cords)

        # Рисуем блик на яблоке.
        highlight_start, highlight_end = self.get_line_cords(
            self.HIGHLIGHT_CORDS, self.position
        )
        pg.draw.line(
            screen,
            self.DEFAULT_COLOR,
            highlight_start,
            highlight_end,
            2
        )


class Snake(GameObject):
    """Класс для игрового объекта 'Змейка'.

    'Змейка' появляется в центре поля, является управляемым игроком объектом,
    цель: съесть 'Яблоко', тем самым увеличиться в размерах.
    """

    SNAKE_COLOR = (59, 150, 97)  # Цвет змейки - светло-зеленый.
    BORDER_COLOR = (46, 135, 83)  # Цвет границы ячейки - зеленый.
    MAX_SPEED = 40  # Максимальная скорость змейки.

    def __init__(
            self,
            body_color: tuple[int, int, int] = SNAKE_COLOR
    ) -> None:
        """Инициализирует экземпляр игрового объекта 'Змейка'
        и задает начальные параметры.
        """
        super().__init__(body_color)
        self.reset(direction=RIGHT)

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает координаты головы (первого сегмента)."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Обновляет текущее направление движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет все координаты списка сегментов 'Змейки' и
        реализует проход сквозь края поля.
        """
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction

        new_head_cords = (
            (head_x + (direction_x * GRID_SIZE)) % SCREEN_WIDTH,
            (head_y + (direction_y * GRID_SIZE)) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head_cords)
        self.last = self.positions[-1]
        if len(self.positions) > self.length:
            del self.positions[-1]

    def reset(self, direction: tuple[int, int] | None = None) -> None:
        """Откатывает параметры 'Змейки' до стартовых, если направление
        движения не передано - выбирает случайным образом.
        """
        self.length = 1
        self.positions = [SCREEN_CENTER]
        self.direction = direction if direction else choice(ALL_DIRECTIONS)
        self.next_direction = None
        self.last = None
        self.speed = SPEED  # Переменная для реализации ускорения змейки.

    def change_speed(self) -> None:
        """Увеличивает скорость 'Змейки' в течение игры.

        Зависит от количества съеденных яблок.
        """
        # Скорость увеличивается на 2 за каждые 3 съеденных яблока.
        calculation = SPEED + (self.length // 3) * 2
        self.speed = (
            calculation if calculation <= self.MAX_SPEED else self.MAX_SPEED
        )

    def draw(self) -> None:
        """Отрисовывает 'Змейку' на игровом поле: отдельно тело и голову,
        а также закрашивает последний, уже не нужный, сегмент.
        """
        # Отрисовка всех сегментов тела змейки.
        for position in self.positions[:-1]:
            self.draw_square(self.body_color, self.BORDER_COLOR, position)

        # Отрисовка головы змейки.
        head = self.get_head_position()
        self.draw_square(self.body_color, self.BORDER_COLOR, head)

        # Затирание последнего сегмента.
        if self.last:
            self.draw_square(
                BOARD_BACKGROUND_COLOR, BOARD_BACKGROUND_COLOR, self.last
            )


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает нажатия клавиш."""
    for event in pg.event.get():
        if event.type == pg.QUIT or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if (
                event.key in (pg.K_UP, pg.K_w)
                and game_object.direction != DOWN
            ):
                game_object.next_direction = UP
            elif (
                event.key in (pg.K_DOWN, pg.K_s)
                and game_object.direction != UP
            ):
                game_object.next_direction = DOWN
            elif (
                event.key in (pg.K_LEFT, pg.K_a)
                and game_object.direction != RIGHT
            ):
                game_object.next_direction = LEFT
            elif (
                event.key in (pg.K_RIGHT, pg.K_d)
                and game_object.direction != LEFT
            ):
                game_object.next_direction = RIGHT


def get_apple_word(amount: int) -> str:
    """Выбирает правильное склонение относительно переданного количества."""
    if amount % 10 == 1 and amount % 100 != 11:
        return 'яблоко'
    elif amount % 10 in (2, 3, 4) and amount % 100 not in (12, 13, 14):
        return 'яблока'
    else:
        return 'яблок'


def main() -> None:
    """Управляет игровым процессом: запускает игру, обрабатывает события,
    обновляет экран.
    """
    pg.init()
    pg.display.set_caption('Змейка  |  ESC - выход')

    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        # Обработка событий.
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка логики.
        snake_head = snake.get_head_position()
        if snake_head == apple.position:
            snake.length += 1

            # Проверка победы
            if snake.length >= GRID_WIDTH * GRID_HEIGHT:
                print(f'Ура! Победа! Счет: {snake.length}.')
                pg.quit()
                raise SystemExit

            snake.change_speed()
            apple.randomize_position(snake.positions)

            apple_amount = snake.length - 1
            apple_word = get_apple_word(apple_amount)
            pg.display.set_caption(
                f'Змейка  |  Счет: {apple_amount} {apple_word}  |  ESC - выход'
            )

        elif snake_head in snake.positions[4:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)
            pg.display.set_caption(
                'Змейка  | Ой, змеино-хвостовое происшествие!  |  ESC - выход'
            )

        # Отрисовка объектов.
        snake.draw()
        apple.draw()

        pg.display.update()
        clock.tick(snake.speed)


if __name__ == '__main__':
    main()
