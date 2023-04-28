#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam


import sys
import math
import itertools
import collections as co
import random
import time
import curses
import locale

DEBUG = False

GRAVITY = 1.0
BLANK_BRAILLE = u'\u2800'


class Body:
    def __init__(self, pos, mass, velocity):
        self.pos = pos
        self.mass = mass
        self.vel = velocity


class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, vec):
        return Vector(self.x + vec.x, self.y + vec.y)

    def __iadd__(self, vec):
        self.x += vec.x
        self.y += vec.y
        return self

    def __sub__(self, vec):
        return Vector(self.x - vec.x, self.y - vec.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)

    def mag(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        return self/self.mag()


def main(scr):
    esetup()
    setup_curses()
    scr.clear()

    # bodies = predefined_bodies()
    bodies = predefined_bodies2()
    # bodies = rand_bodies()
    screen_buf = clear_buf()
    t = 0
    freq = 100
    dt = 1.0/freq
    step = 0

    while not check_exit_key(scr, step):
        calcs(bodies, dt)

        for b in bodies:
            draw_pt(screen_buf, b.pos)
        draw_info(screen_buf,  '[%05.2f]: %8.4f %8.4f' % (t, bodies[1].pos.x, bodies[1].pos.y))
        show(scr, screen_buf)

        time.sleep(dt)
        t += dt
        step += 1


def esetup():
    """ Hard-coded console for debug prints (std err).
    Console must exist before running script. """
    if DEBUG:
        sys.stderr = open('/dev/pts/1', 'w')


def eprint(*args, **kwargs):
    """ Debug print function (on std err) """
    if DEBUG:
        print(*args, file=sys.stderr)


def setup_curses():
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)


def check_exit_key(scr, step):
    """ Wait for key (defined by halfdelay), and check if q """
    # getch() is very slow, so check every 200 steps only
    if step % 200:
        return False

    ch = scr.getch()
    return ch == ord('q')


def predefined_bodies():
    bodies = [
        Body(pos=Vector(110, 80), mass=10000, velocity=Vector(0, 0)),
        Body(pos=Vector(50, 100), mass=10, velocity=Vector(12, 3)),
        Body(pos=Vector(95, 80), mass=1, velocity=Vector(9, 21))
    ]

    return bodies


def predefined_bodies2():
    bodies = [
        Body(pos=Vector(110, 80), mass=10000, velocity=Vector(0, 0)),
        Body(pos=Vector(50, 100), mass=10, velocity=Vector(12, 3)),
        Body(pos=Vector(95, 80), mass=1, velocity=Vector(9, 21)),
        Body(pos=Vector(145, 120), mass=104, velocity=Vector(-9, -20))
    ]

    return bodies


def rand_bodies():
    bodies = []
    for i in range(5):
        pos = Vector(random.randint(0, curses.COLS), random.randint(0, curses.LINES))
        mass = random.randint(1, 1000)
        velocity = Vector(random.randint(-25, 25), random.randint(-25, 25))
        bodies.append(Body(pos, mass, velocity))

    bodies[0].mass = 10000

    return bodies


def clear_buf():
    return [list(BLANK_BRAILLE * (curses.COLS - 1)) for _ in range(curses.LINES)]


def draw_info(screen_buf, s):
    screen_buf[0] = list(s) + screen_buf[0][len(s):]


def draw_pt(screen_buf, pt):
    x = int(pt.x / 2)
    y = curses.LINES - 1 - int(pt.y / 4)

    if pt.y < 0 or y < 0 or pt.x < 0 or x >= curses.COLS - 1:
        return

    uchar = ord(screen_buf[y][x])
    screen_buf[y][x] = unicode_char(uchar | relative_uchar(pt))


def unicode_char(param):
    if sys.version_info[0] == 2:
        return unichr(param)
    return chr(param)


def relative_uchar(pt):
    bx = int(pt.x) % 2
    by = int(pt.y) % 4

    if bx == 0:
        if by == 0:
            return 0x40
        else:
            return 0x4 >> (by - 1)
    else:
        if by == 0:
            return 0x80
        else:
            return 0x20 >> (by -1)


def show(scr, screen_buf):
    for num, line in enumerate(screen_buf):
        scr.addstr(num, 0, u''.join(line).encode('utf-8'))

    scr.refresh()


def calcs(bodies, dt):
    forces = co.defaultdict(Vector)

    for idx1, idx2 in itertools.combinations(range(len(bodies)), 2):
        f1, f2 = calc_forces(bodies[idx1], bodies[idx2], dt)
        forces[idx1] += f1
        forces[idx2] += f2

    for idx, b in enumerate(bodies):
        b.acc = forces[idx] / b.mass
        b.vel = b.vel + (b.acc * dt)
        b.pos = b.pos + (b.vel * dt)


def calc_forces(body1, body2, dt):
    dist = distance(body1.pos, body2.pos)
    if dist < 1:
        exit()

    dir1 = (body2.pos - body1.pos).normalize()
    dir2 = (body1.pos - body2.pos).normalize()
    grav_mag = (GRAVITY * body1.mass * body2.mass) / (dist**2)
    force1 = dir1 * grav_mag
    force2 = dir2 * grav_mag

    return force1, force2


def distance(vec1, vec2):
    return math.sqrt((vec1.x - vec2.x)**2 + (vec1.y - vec2.y)**2)


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
