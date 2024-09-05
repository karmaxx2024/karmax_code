from time import sleep
import curses
import random


class TerminalRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.height, self.width = screen.getmaxyx()
        curses.curs_set(0)  # отключить курсор
        screen.nodelay(1)  # чтобы getch не ждал кнопки

        self.clear()

    def clear(self):
        self.screen.clear()

    def set_pixel(self, x, y, symbol):
        x = round(x)
        y = round(y)
        x = min(max(x, 0), self.width - 1)
        y = min(max(y, 0), self.height - 1)
        if x + y < self.width + self.height - 2:
            self.screen.addch(y, x, symbol)

    def hor_line(self, x1, x2, y, symbol):
        [self.set_pixel(x, y, symbol) for x in range(x1, x2 + 1)]

    def ver_line(self, x, y1, y2, symbol):
        [self.set_pixel(x, y, symbol) for y in range(y1, y2 + 1)]

    def print(self, x, y, text):
        [self.set_pixel(cx, y, symbol) for cx, symbol in zip(range(x, self.width), text)]


class Pong:
    def __init__(self, r: TerminalRenderer):
        self._renderer = r
        w, h = r.width, r.height

        # позиция мяча
        self.x, self.y = w // 2, h // 2

        # скорости мяча
        self.dx = w / h * 0.1
        self.randomize_dx()

        self.dy_amp = 0.5
        self.randomize_dy()

        # ракетки игрока и робота
        self.racket_size = 6
        self.robot_pos = self.my_pos = h // 2 - self.racket_size // 2

        # счет
        self.my_score = self.robot_score = 0
        self.goal = False

    def randomize_dy(self):
        self.dy = random.uniform(-self.dy_amp, self.dy_amp)

    def randomize_dx(self):
        self.dx = random.choice([self.dx, -self.dx])

    def _robot_ai(self):
        w, h = self._renderer.width, self._renderer.height

        if self.x > w / 2:
            p = self.robot_pos - random.uniform(0.1, 0.2) * (self.robot_pos + self.racket_size / 2 - self.y)
            self.robot_pos = max(min(round(p), h - 2 - self.racket_size), 1)

    def step(self, input_key):
        w, h = self._renderer.width, self._renderer.height

        self._robot_ai()

        if input_key == ord('w'):
            self.my_pos = max(self.my_pos - 1, 1)
        elif input_key == ord('s'):
            self.my_pos = min(self.my_pos + 1, h - 2 - self.racket_size)

        self.x += self.dx
        self.y += self.dy

        # удар о ракетку игрока
        hit_robot = self.x > w - 1 and (self.robot_pos <= self.y <= self.robot_pos + self.racket_size)
        hit_me = self.x < 1 and (self.my_pos <= self.y <= self.my_pos + self.racket_size)

        if hit_me or hit_robot:
            self.x -= self.dx
            self.dx = -self.dx
            self.randomize_dy()
        # вылет за пределы поля
        elif self.x <= 1 or self.x >= w - 1:
            if self.x <= 1:
                self.robot_score += 1
            else:
                self.my_score += 1

            self.x, self.y = w // 2, h // 2

            self.randomize_dx()
            self.randomize_dy()

            self.goal = True

        # горизонтальные стенки
        if self.y < 1 or self.y >= h - 2:
            self.y -= self.dy
            self.dy = -self.dy

    def render(self):
        r = self._renderer
        r.clear()
        r.set_pixel(self.x, self.y, 'o')

        r.hor_line(1, r.width - 1, 0, '#')
        r.hor_line(1, r.width - 1, r.height - 1, '#')
        r.print(1, 0, 'W = up ')
        r.print(1, r.height - 1, 'S = down ')

        title = f'  {self.my_score}  -  PONG  -  {self.robot_score}  '
        r.print(r.width // 2 - len(title) // 2, 0, title)

        r.ver_line(0, self.my_pos, self.my_pos + self.racket_size, '|')
        r.ver_line(r.width - 1, self.robot_pos, self.robot_pos + self.racket_size, '|')

        if self.goal:
            self.goal = False
            r.print(self.x - 2, self.y, 'GOAL')
            r.screen.refresh()
            sleep(1.0)

        # поспим для стабильности картинки
        sleep(0.01)


def main(screen):
    r = TerminalRenderer(screen)
    p = Pong(r)

    while True:
        c = screen.getch()
        if c == 27:  # Escape
            break

        p.step(c)
        p.render()


curses.wrapper(main)


