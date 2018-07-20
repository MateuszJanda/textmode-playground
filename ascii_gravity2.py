#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import math
import itertools
import time
import curses
import locale


G = 1.0


def main(scr):
    setup()
    scr.clear()

    bodies = [
        Body(pos=Vector(110, 80), mass=10000, velocity=Vector(0, 0)),
        Body(pos=Vector(50, 100), mass=10, velocity=Vector(12, 3)),
        Body(pos=Vector(95, 80), mass=1, velocity=Vector(9, 21))
    ]

    t = 0
    freq = 100
    dt = 1.0/freq
    screen_buf = clear_buf()

    while True:
        calcs(bodies, dt)

        for b in bodies:
            draw_pt(screen_buf, b.pos)
        draw_info(screen_buf,  '[%.2f]: %.4f %.4f' % (t, bodies[1].pos.x, bodies[1].pos.y))
        display(scr, screen_buf)

        time.sleep(0.01)
        t += dt

    curses.endwin()


def setup():
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(5)
    curses.noecho()
    curses.curs_set(False)


def clear_buf():
    return [list(u'\u2800' * (curses.COLS - 1)) for _ in range(curses.LINES)]


def draw_info(screen_buf, s):
    padding = curses.COLS - len(s) - 1
    screen_buf[0] = list(s) + screen_buf[0][padding:]


def draw_pt(screen_buf, pt):
    x = int(pt.x / 2)
    y = curses.LINES - 1 - int(pt.y / 4)

    if pt.y < 0 or y < 0 or pt.x < 0 or x >= curses.COLS - 1:
        return

    uchar = ord(screen_buf[y][x])
    screen_buf[y][x] = unichr(uchar | relative_uchar(pt))


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


def display(scr, screen_buf):
    for num, line in enumerate(screen_buf):
        scr.addstr(num, 0, u''.join(line).encode('utf-8'))

    scr.refresh()


def calcs(bodies, dt):
    for b in bodies:
        b.forces = Vector(0, 0)

    for b1, b2 in itertools.combinations(bodies, 2):
        calc_forces(b1, b2, dt)

    for b in bodies:
        b.acc = b.forces / b.mass
        b.vel = b.vel + (b.acc * dt)
        b.pos = b.pos + (b.vel * dt)


def calc_forces(body1, body2, dt):
    dist = magnitude(body1.pos, body2.pos)
    if dist < 1:
        exit()

    dir1 = normalize(body2.pos - body1.pos)
    dir2 = normalize(body1.pos - body2.pos)
    grav_mag = (G * body1.mass * body2.mass) / (dist**2)
    body1.forces = body1.forces + (dir1 * grav_mag)
    body2.forces = body2.forces + (dir2 * grav_mag)


class Body:
    def __init__(self, pos, mass, velocity):
        self.pos = pos
        self.mass = mass
        self.vel = velocity


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, vec):
        return Vector(self.x + vec.x, self.y + vec.y)

    def __sub__(self, vec):
        return Vector(self.x - vec.x, self.y - vec.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)


def magnitude(vec1, vec2):
    return math.sqrt((vec1.x - vec2.x)**2 + (vec1.y - vec2.y)**2)


def normalize(vec):
    mag = magnitude(Vector(0, 0), vec)
    return Vector(vec.x / mag, vec.y / mag)


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
