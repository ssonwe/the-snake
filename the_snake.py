from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

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

# Настройка и заголовок игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Центр поля.
    DEFAULT_COLOR = (255, 255, 255)  # Цвет по умолчанию - белый.

    def __init__(
            self,
            body_color: tuple[int, int, int] = DEFAULT_COLOR
    ) -> None:
        """Инициализирует игровой объект в центре поля."""
        self.position = self.SCREEN_CENTER
        self.body_color = body_color

    def draw(self) -> None:
        """Отрисовывает игровые объекты (реализация в дочерних классах)."""
        pass


class Apple(GameObject):
    """Класс для игрового объекта 'Яблоко'.

    'Яблоко' спавнится на случайных координатах поля,
    является целью для игрового объекта 'Змейка'.
    """

    APPLE_COLOR = (235, 78, 61)  # Цвет яблока - красный.
    BORDER_COLOR = (214, 64, 47)  # Цвет границы ячейки - темно-красный.

    def __init__(
            self,
            body_color: tuple[int, int, int] = APPLE_COLOR
    ) -> None:
        """Инициализирует экземпляр игрового объекта 'Яблоко'
        и создает случайные стартовые координаты.
        """
        super().__init__(body_color)
        self.randomize_position()

    def randomize_position(self) -> None:
        """Определяет новые координаты 'Яблока' случайнм образом."""
        # Отнимаем 1, так как нумерация клеток идет от 0 до 31 и от 0 до 23,
        # при 32(x) и 24(y) клетках, на которые поделено поле.
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self) -> None:
        """Отрисовывает 'Яблоко' на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, self.BORDER_COLOR, rect, 1)


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
        self.length = 1
        self.positions = [self.SCREEN_CENTER]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.speed = SPEED  # Переменная для реализации ускорения змейки.

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

        new_head_cords = (
            (head_x + (self.direction[0] * GRID_SIZE)) % SCREEN_WIDTH,
            (head_y + (self.direction[1] * GRID_SIZE)) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head_cords)
        self.last = self.positions[-1]
        if len(self.positions) > self.length:
            del self.positions[-1]

    def reset(self) -> None:
        """Откатывает параметры 'Змейки' до стартовых, но
        направление движения выбирает случайным образом.
        """
        self.length = 1
        self.positions = [self.SCREEN_CENTER]
        self.direction = choice(ALL_DIRECTIONS)
        self.next_direction = None
        self.last = None
        self.speed = SPEED

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
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, self.BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки.
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, self.BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента.
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает нажатия клавиш."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if (
                event.key in (pygame.K_UP, pygame.K_w)
                and game_object.direction != DOWN
            ):
                game_object.next_direction = UP
            elif (
                event.key in (pygame.K_DOWN, pygame.K_s)
                and game_object.direction != UP
            ):
                game_object.next_direction = DOWN
            elif (
                event.key in (pygame.K_LEFT, pygame.K_a)
                and game_object.direction != RIGHT
            ):
                game_object.next_direction = LEFT
            elif (
                event.key in (pygame.K_RIGHT, pygame.K_d)
                and game_object.direction != LEFT
            ):
                game_object.next_direction = RIGHT


def main() -> None:
    """Управляет игровым процессом: запускает игру, обрабатывает события,
    обновляет экран.
    """
    pygame.init()
    apple = Apple()
    snake = Snake()

    while True:
        # Обработка событий.
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка логики.
        snake_head = snake.get_head_position()
        if snake_head == apple.position:
            snake.length += 1
            apple.randomize_position()
            while apple.position in snake.positions:
                apple.randomize_position()

        if snake_head in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.change_speed()

        # Отрисовка объектов.
        snake.draw()
        apple.draw()

        pygame.display.update()
        clock.tick(snake.speed)


if __name__ == '__main__':
    main()
