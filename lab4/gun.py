import numpy as np
import pygame as pg
from random import randint
import time

pg.init()
pg.font.init()

BLACK = (0, 0, 0)
ORANGE = (252, 148, 7)
WHITE = (255, 255, 255)

SCREEN_SIZE = (800, 600)


def rand_color():  # случайный цвет
    return (randint(0, 255), randint(0, 255), randint(0, 255))


class GameObject:
    pass


class Bullet(GameObject):  # создаем класс пули

    def __init__(self, coord, vel, rad=20, color=None):

        self.coord = coord  # задаем координаты
        self.vel = vel  # задаем скорости по x и y
        if color is None:
            color = rand_color()  # задаем цвет
        self.color = color
        self.rad = rad  # задаем радиус
        self.is_alive = True  # задаем, что объект существует

    def wall_collision(self, refl_ort=0.8, refl_par=0.9):
        # обработка столкновения со стенами

        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1 - i] = int(self.vel[1 - i] * refl_par)
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1 - i] = int(self.vel[1 - i] * refl_par)

    def move(self, time=1, grav=0):
        # обработка движения под действием гравитации

        self.vel[1] += grav
        for i in range(2):
            self.coord[i] += time * self.vel[i]
        self.wall_collision()
        if (self.vel[0] ** 2 + self.vel[1] ** 2 < 2 ** 2 and
                self.coord[1] > SCREEN_SIZE[1] - 2 * self.rad):
            self.is_alive = False

    def draw(self, screen):  # прорисовка пули

        pg.draw.circle(screen, self.color, self.coord, self.rad)


class Cannon(GameObject):  # класс пушки

    def __init__(self, coord=None, angle=0,
                 max_pow=70, min_pow=20, color=BLACK):

        if coord is None:
            coord = [30, SCREEN_SIZE[1] * 0.9]
        self.coord = coord  # задаем координаты
        self.angle = angle  # задаем угол
        self.max_pow = max_pow  # задаем максимальную мощность выстрела
        self.min_pow = min_pow  # задаем минимальную мощность выстрела
        self.color = color  # задаем цвет
        self.active = False  # задаем статус активности
        self.pow = min_pow

    def activate(self):  # меняет статус пушки на активный

        self.active = True

    def gain(self, inc=2):  # накопление "мощности"

        if self.active and self.pow < self.max_pow:
            self.pow += inc
            self.color = ORANGE

    def shoot(self):  # производит выстрел

        vel = self.pow
        angle = self.angle
        ball = Bullet(list(self.coord), [int(vel * np.cos(angle)),
                                         int(vel * np.sin(angle))])
        self.pow = self.min_pow
        self.active = False
        return ball

    def set_angle(self, target_pos):
        # задает угол, под которым производится выстрел

        self.angle = np.arctan2(target_pos[1] - self.coord[1],
                                target_pos[0] - self.coord[0])

    def move_y(self, inc):  # изменяет позицию пушки по вертикали

        if ((self.coord[1] > 30 or inc > 0) and
                (self.coord[1] < SCREEN_SIZE[1] - 30 or inc < 0)):
            self.coord[1] += inc

    def move_x(self, inc):  # изменяет позицию пушки по вертикали

        if ((self.coord[0] > 30 or inc > 0) and
                (self.coord[0] < SCREEN_SIZE[1] - 30 or inc < 0)):
            self.coord[0] += inc

    def draw(self, screen):  # прорисовывает пушку

        gun_shape = []
        vec_1 = np.array([int(5 * np.cos(self.angle - np.pi / 2)),
                          int(5 * np.sin(self.angle - np.pi / 2))])
        vec_2 = np.array([int(self.pow * np.cos(self.angle)),
                          int(self.pow * np.sin(self.angle))])
        gun_pos = np.array(self.coord)
        gun_shape.append((gun_pos + vec_1).tolist())
        gun_shape.append((gun_pos + vec_1 + vec_2).tolist())
        gun_shape.append((gun_pos + vec_2 - vec_1).tolist())
        gun_shape.append((gun_pos - vec_1).tolist())
        pg.draw.polygon(screen, self.color, gun_shape)


class Target(GameObject):  # класс цели

    def __init__(self, coord=None, color=None, rad=30):

        if coord is None:
            coord = [randint(rad, SCREEN_SIZE[0] - rad),
                     randint(rad, SCREEN_SIZE[1] - rad)]  # задаем координаты
        self.coord = coord
        self.rad = rad  # задаем радиус

        if color is None:
            color = rand_color()  # задаем цвет
        self.color = color

    def check_collision(self, ball):  # проверка на попадание пули по цели

        dist = sum([(self.coord[i] - ball.coord[i]) ** 2 for i in range(2)]) ** 0.5
        min_dist = self.rad + ball.rad
        return dist <= min_dist

    def draw(self, screen):  # прорисовка цели

        pg.draw.circle(screen, self.color, self.coord, self.rad)

    def move(self):  # данная цель не двигается

        pass


class MovingTarget(Target):  # класс движущейся цели
    def __init__(self, coord=None, color=None, rad=30):
        super().__init__(coord, color, rad)
        self.vx = randint(-2, +2)  # задаем скорость по x
        self.vy = randint(-2, +2)  # задаем скорость по y

    def wall_collision(self):
        # обработка столковения цели со стенами
        if 30 > self.coord[0] or SCREEN_SIZE[0] - 30 < self.coord[0]:
            self.vx = -self.vx
        if 30 > self.coord[1] or SCREEN_SIZE[1] - 30 < self.coord[1]:
            self.vy = -self.vy

    def move(self):  # обработка движения цели
        self.wall_collision()
        self.coord[0] += self.vx
        self.coord[1] += self.vy


class Results:  # класс с результатами игры

    def __init__(self, t_destr=0, b_used=0):
        self.t_destr = t_destr  # количество пораженных целей
        self.b_used = b_used  # количество потраченных пуль
        self.font = pg.font.SysFont('freesansbold.ttf', 25)  # задаем шрифт

    def score(self):  # подсчет количества очков для усложнения игры

        return self.t_destr - self.b_used

    def draw_score(self, screen):  # счетчик очков
        score_surf = (self.font.render("{}".format(self.t_destr), True, BLACK))
        screen.blit(score_surf, [10, 10])

    def draw_endgame(self, screen):  # окно конца игры
        score_surf = (self.font.render(
            "Вы уничтожили цели за {} выстрелов".format(self.b_used),
            True, BLACK))
        start_time = time.time()
        while (time.time() - start_time < 3):
            screen.blit(score_surf, [SCREEN_SIZE[0] // 3, SCREEN_SIZE[1] // 2])
            pg.display.update()


class Manager:  # класс игрового менеджера

    def __init__(self, n_targets=1):
        self.balls = []
        self.gun = Cannon()
        self.targets = []
        self.score_t = Results()
        self.n_targets = n_targets
        self.new_mission()

    def new_mission(self):  # начало игры с постепенным усложнением

        for i in range(self.n_targets):
            self.targets.append(Target(rad=randint(
                max(1, 30 - 2 * max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))
        for i in range(self.n_targets):
            self.targets.append(MovingTarget(rad=randint(
                max(1, 30 - 2 * max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))

    def process(self, events, screen):
        # функция, контроллирующая все игровые процессы

        done = self.handle_events(events)

        if pg.mouse.get_focused():
            mouse_pos = pg.mouse.get_pos()
            self.gun.set_angle(mouse_pos)

        self.move()
        self.collide()
        self.draw(screen)

        if ((len(self.targets) == 0 and len(self.balls) == 0)
                or len(self.targets) == 0):
            self.balls = []
            self.score_t.draw_endgame(screen)
            self.new_mission()

        return done

    def handle_events(self, events):
        # обрабатывает ввод с мыши и клавиатуры
        # (обеспечивает выстрел и перемещение пушки)

        done = False
        for event in events:
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.gun.move_y(-5)
                elif event.key == pg.K_DOWN:
                    self.gun.move_y(5)
                elif event.key == pg.K_LEFT:
                    self.gun.move_x(-5)
                elif event.key == pg.K_RIGHT:
                    self.gun.move_x(5)
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.gun.activate()
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.balls.append(self.gun.shoot())
                    self.score_t.b_used += 1
                    self.gun.color = BLACK
        return done

    def draw(self, screen):
        # прорисовка пули, пушки, целей, счетчик очков и окно конца игры

        for ball in self.balls:
            ball.draw(screen)
        for target in self.targets:
            target.draw(screen)
        self.gun.draw(screen)
        self.score_t.draw_score(screen)

    def move(self):
        # отвечает за перемещение пули и пушки, убирает "мертвые" пули

        dead_balls = []
        for i, ball in enumerate(self.balls):
            ball.move(grav=2)
            if not ball.is_alive:
                dead_balls.append(i)
        for i in reversed(dead_balls):
            self.balls.pop(i)
        for i, target in enumerate(self.targets):
            target.move()
        self.gun.gain()

    def collide(self):  # проверка на попадание пуль по целям

        collisions = []
        targets_c = []
        for i, ball in enumerate(self.balls):
            for j, target in enumerate(self.targets):
                if target.check_collision(ball):
                    collisions.append([i, j])
                    targets_c.append(j)
        targets_c.sort()
        for j in reversed(targets_c):
            self.score_t.t_destr += 1
            self.targets.pop(j)


screen = pg.display.set_mode(SCREEN_SIZE)  # создаем экран

done = False
clock = pg.time.Clock()

mgr = Manager(n_targets=3)  # создаем игровой менеджер 

while not done:
    clock.tick(20)
    screen.fill(WHITE)

    done = mgr.process(pg.event.get(), screen)  # запуск игры

    pg.display.flip()

pg.quit()

