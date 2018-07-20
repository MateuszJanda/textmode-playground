#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import math
import time
import curses
import locale


G = 19.0


def main(scr):
    setup()
    scr.clear()

    star = Body(pos=Vector(100, 80), mass=1000, velocity=Vector(0, 0))
    # satellite = Body(pos=Vector(50, 40), mass=1, velocity=Vector(4, 10))
    # satellite = Body(pos=Vector(120, 40), mass=1, velocity=Vector(14, 7))
    # satellite = Body(pos=Vector(30, 40), mass=1, velocity=Vector(4, 19))
    satellite = Body(pos=Vector(30, 40), mass=1, velocity=Vector(15, 25))

    star = Body(pos=Vector(100, 80), mass=1000, velocity=Vector(0, 0))
    satellite = Body(pos=Vector(50, 40), mass=1, velocity=Vector(14, 7))


    t = 0
    freq = 100
    dt = 1.0/freq
    step = 0

    screen_buf = clear_buf()
    while not check_exit_key(scr, step):
        distance = magnitude(star.pos, satellite.pos)
        if distance <= 1:
            break

        calcs(star, satellite, dt)

        draw_pt(screen_buf, star.pos)
        draw_pt(screen_buf, satellite.pos)

        # draw_debug(screen_buf, str(step))
        display(scr, screen_buf)

        time.sleep(dt)
        t += dt
        step += 1

    curses.endwin()


def setup():
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.noecho()
    curses.curs_set(False)


def check_exit_key(scr, step):
    # getch is very slow, so check every 200 steps only
    if step % 200:
        return False
    # Wait for key (defined by halfdelay), and check his code
    ch = scr.getch()
    return ch == ord('q')


def clear_buf():
    return [list(u'\u2800' * (curses.COLS - 1)) for _ in range(curses.LINES)]


def draw_pt(screen_buf, pt):
    x = int(pt.x / 2)
    y = curses.LINES - 1 - int(pt.y / 4)

    draw_debug(screen_buf, str(y) + ',   ' + str(pt.y) + ',   ' + str(curses.LINES))
    if pt.y < 0 or y < 0 or pt.x < 0 or x >= curses.COLS - 1:
        return

    uchar = ord(screen_buf[y][x])
    screen_buf[y][x] = unichr(uchar | relative_uchar(pt))


def draw_debug(screen_buf, s):
    padding = curses.COLS - len(s) - 1
    screen_buf[0] = list(s + padding * u'\u2800')


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


def calcs(star, satellite, dt):
    distance = magnitude(star.pos, satellite.pos)
    direction = normalize(sub(star.pos, satellite.pos))
    Fg = mul_s(direction, (G * star.mass * satellite.mass) / (distance**2))

    satellite.acc = div_s(Fg, satellite.mass)
    satellite.vel = add(satellite.vel, mul_s(satellite.acc, dt))
    satellite.pos = add(satellite.pos, mul_s(satellite.vel, dt))


class Body:
    def __init__(self, pos, mass, velocity):
        self.pos = pos
        self.mass = mass
        self.vel = velocity


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def magnitude(vec1, vec2):
    return math.sqrt((vec1.x - vec2.x)**2 + (vec1.y - vec2.y)**2)


def normalize(vec):
    mag = magnitude(Vector(0, 0), vec)
    return Vector(vec.x / mag, vec.y / mag)


def mul_s(vec, s):
    return Vector(vec.x * s, vec.y * s)


def div_s(vec, s):
    return Vector(vec.x / s, vec.y / s)


def sub(vec1, vec2):
    return Vector(vec1.x - vec2.x, vec1.y - vec2.y)


def add(vec1, vec2):
    return Vector(vec1.x + vec2.x, vec1.y + vec2.y)


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
