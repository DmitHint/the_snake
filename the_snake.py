import pygame
import os
from random import choice

HIGH_SCORE_FILE = 'highscore.txt'


def load_high_score():
    """
    Загружает рекорд из файла, возвращает 0,
    если файл не существует или пуст.
    """
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as file:
            try:
                return int(file.read().strip())
            except ValueError:
                return 0
    return 0


def save_high_score(score):
    """Сохраняет рекорд в файл."""
    with open(HIGH_SCORE_FILE, 'w') as file:
        file.write(str(score))


# Константы для размеров поля и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
INFO_BAR_HEIGHT = 40

ALL_CELLS = set((x * GRID_SIZE, y * GRID_SIZE)
                for x in range(GRID_WIDTH)
                for y in range(GRID_HEIGHT))

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
BAD_FOOD_COLOR = (255, 165, 0)
SNAKE_COLOR = (0, 255, 0)
OBSTACLE_COLOR = (128, 128, 128)
INFO_TEXT_COLOR = (255, 255, 255)

# Скорость
SPEED = 10

# Настройка игрового окна
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT + INFO_BAR_HEIGHT)
)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()

# Инициализация шрифтов
pygame.font.init()
font = pygame.font.SysFont('Arial', 24)


def get_available_positions(snake_positions):
    """
    Возвращает множество свободных позиций на поле,
    исключая занятые телом змеи.
    """
    return ALL_CELLS - set(snake_positions)


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=(0, 0), color=(255, 255, 255)):
        self.position = position
        self.body_color = color

    def draw(self):
        """Отрисовка объекта на текущей позиции."""
        self.draw_at_position(self.position, self.body_color)

    @staticmethod
    def draw_at_position(position, color):
        """Отрисовка объекта на заданной позиции."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс для яблока."""

    def __init__(self, snake_positions=[]):
        self.randomize_position(snake_positions)
        super().__init__(self.position, APPLE_COLOR)

    def randomize_position(self, snake_positions):
        """
        Генерация случайной позиции для яблока,
        исключая занятые клетки змеи.
        """
        available_positions = get_available_positions(snake_positions)
        self.position = choice(list(available_positions))


class BadFood(GameObject):
    """Класс для неправильной еды."""

    def __init__(self, snake_positions=[]):
        self.randomize_position(snake_positions)
        super().__init__(self.position, BAD_FOOD_COLOR)

    def randomize_position(self, snake_positions):
        """Генерация случайной позиции для неправильной еды."""
        available_positions = get_available_positions(snake_positions)
        self.position = choice(list(available_positions))


class Obstacle(GameObject):
    """Класс для препятствий."""

    def __init__(self, snake_positions=[]):
        self.randomize_position(snake_positions)
        super().__init__(self.position, OBSTACLE_COLOR)

    def randomize_position(self, snake_positions):
        """Генерация случайной позиции для препятствия."""
        available_positions = get_available_positions(snake_positions)
        self.position = choice(list(available_positions))


class Snake(GameObject):
    """Класс для змейки, наследующийся от GameObject."""

    def __init__(self):
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        super().__init__(self.positions[0], SNAKE_COLOR)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновляет направление змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Двигает змейку в соответствии с текущим направлением."""
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + (x * GRID_SIZE)) % SCREEN_WIDTH,
               (cur[1] + (y * GRID_SIZE)) % SCREEN_HEIGHT)

        if new in self.positions[1:]:
            self.reset()
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.last = self.positions.pop()
            else:
                self.last = None

        self.position = self.positions[0]

    def reset(self):
        """Сброс состояния змейки при столкновении с собой или препятствием."""
        self.__init__()

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        for position in self.positions:
            GameObject.draw_at_position(position, self.body_color)


def handle_keys(snake, current_speed):
    """Обрабатывает нажатия клавиш."""
    # Словарь для сопоставления клавиш с новыми направлениями
    direction_map = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            elif event.key == pygame.K_q:
                current_speed += 2
            elif event.key == pygame.K_w:
                current_speed = max(1, current_speed - 2)
            else:
                # Получаем новое направление из словаря
                new_direction = direction_map.get(event.key)
                snake.next_direction = new_direction

    return current_speed


def draw_info_bar(snake_length, current_speed):
    """Отрисовывает информационную строку над игровым полем."""
    text = f"Length: {snake_length} | Speed: {current_speed}"
    info_surface = font.render(text, True, INFO_TEXT_COLOR)
    screen.fill((0, 0, 0), (0, 0, SCREEN_WIDTH, INFO_BAR_HEIGHT))
    screen.blit(info_surface, (10, 10))


def change_title(snake_length):
    """
    Обновляет заголовок окна с рекордом,
    если текущая длина змейки больше рекорда.
    """
    high_score = load_high_score()
    if snake_length > high_score:
        save_high_score(snake_length)
        pygame.display.set_caption(f'Змейка (Рекорд: {snake_length})')
    else:
        pygame.display.set_caption(f'Змейка (Рекорд: {high_score})')


def main():
    """Основная игровая логика."""
    pygame.init()

    snake = Snake()
    apple = Apple(snake.positions)
    bad_food = BadFood(snake.positions)
    obstacle = Obstacle(snake.positions)
    current_speed = SPEED
    change_title(snake.length)

    while True:
        clock.tick(current_speed)
        current_speed = handle_keys(snake, current_speed)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        if snake.get_head_position() == bad_food.position:
            if snake.length > 1:
                snake.length -= 1
                snake.positions.pop()
            else:
                change_title(snake.length)
                snake.reset()
            bad_food.randomize_position(snake.positions)

        if snake.get_head_position() == obstacle.position:
            change_title(snake.length)
            snake.reset()
            obstacle.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR,
                    (0, INFO_BAR_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
                    )
        draw_info_bar(snake.length, current_speed)
        apple.draw()
        bad_food.draw()
        obstacle.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
