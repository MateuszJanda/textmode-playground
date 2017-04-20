#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import math
import itertools
import random
import time
import curses
import locale


locale.setlocale(locale.LC_ALL, '')
G = 19.0


def main():
    scr = setup()

    # star = Body(pos=Vector(100, 80), mass=10000, velocity=Vector(0, 0))
    # satellite = Body(pos=Vector(120, 40), mass=1, velocity=Vector(14, 7))

    # star = Body(pos=Vector(100, 80), mass=10000, velocity=Vector(0, 0))
    # satellite = Body(pos=Vector(30, 40), mass=1, velocity=Vector(4, 19))

    # star = Body(pos=Vector(100, 80), mass=10000, velocity=Vector(0, 0))
    # satellite = Body(pos=Vector(30, 40), mass=1, velocity=Vector(15, 25))

    # star = Body(pos=Vector(100, 80), mass=1000, velocity=Vector(0, 0))
    # satellite = Body(pos=Vector(80, 40), mass=1, velocity=Vector(4, 17))

    # star = Body(pos=Vector(100, 80), mass=1000, velocity=Vector(0, 0))
    # satellite = Body(pos=Vector(80, 40), mass=1, velocity=Vector(14, -17))
    # satellite2 = Body(pos=Vector(80, 40), mass=1, velocity=Vector(14, -17))

    # star = Body(pos=Vector(100, 80), mass=10000, velocity=Vector(0, 0))
    # satellite = Body(pos=Vector(30, 40), mass=1, velocity=Vector(5, 35))
    # satellite2 = Body(pos=Vector(80, 40), mass=300, velocity=Vector(14, -17))

    star = Body(pos=Vector(100, 80), mass=1000, velocity=Vector(0, 6))
    satellite = Body(pos=Vector(90, 120), mass=1, velocity=Vector(15, 5))
    satellite2 = Body(pos=Vector(40, 100), mass=10, velocity=Vector(-14, -7))


    star2 = Body(pos=Vector(20, 120), mass=1000, velocity=Vector(0, -4))

    bodies = [ Body(pos=Vector(random.randint(0, (curses.LINES - 1) * 4),
                               random.randint(0, (curses.COLS - 1) * 2)),
                    mass=random.randint(1, 2),
                    velocity=Vector(random.randint(-10, 10),
                                    random.randint(-10, 10))) for _ in range(20)]

    bodies[0].mass = 2000
    bodies[0].vel = Vector(0, 0)

    t = 0
    freq = 100
    dt = 1.0/freq

    screen_buf = clear_buf()


    while True:
        distance = magnitude(star.pos, satellite.pos)
        if distance <= 1:
            break

        distance = magnitude(satellite.pos, satellite2.pos)
        if distance <= 1:
            break

        # calcs(star, satellite, dt)
        # calcs(star, satellite2, dt)
        # calcs2(star, satellite2, satellite, dt)
        # calcs2(star, satellite, satellite2, dt)

        # calcs(satellite, satellite2, dt)
        # calcs(satellite2, satellite, dt)


        # prev_cals([star, satellite, satellite2, star2], dt)
        # prev_cals([star, satellite, satellite2, star2], dt)
        prev_cals(bodies, dt)

        for b in bodies:
            draw_pt(screen_buf, b.pos)
        # draw_pt(screen_buf, star.pos)
        # draw_pt(screen_buf, star2.pos)
        # draw_pt(screen_buf, satellite.pos)
        # draw_pt(screen_buf, satellite2.pos)
        display(scr, screen_buf)

        # time.sleep(0.01)
        t += dt

    curses.endwin()


def setup():
    scr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(5)
    curses.noecho()
    curses.curs_set(False)
    scr.clear()
    return scr


def clear_buf():
    return [list(u'\u2800' * (curses.COLS - 1)) for _ in range(curses.LINES)]


def draw_pt(screen_buf, pt):
    x = int(pt.x / 2)
    y = curses.LINES - 1 - int(pt.y / 4)

    # if y < 0 or y >= curses.LINES or x < 0 or x >= curses.COLS - 1:
        # return
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


def calcs(star, satellite, dt):
    distance = magnitude(star.pos, satellite.pos)
    direction = normalize(sub(star.pos, satellite.pos))
    Fg = mul_s(direction, (G * star.mass * satellite.mass) / (distance**2))

    satellite.acc = div_s(Fg, satellite.mass)
    satellite.vel = add(satellite.vel, mul_s(satellite.acc, dt))
    satellite.pos = add(satellite.pos, mul_s(satellite.vel, dt))


def calcs2(star, satellite, satellite2, dt):
    dist_star1 = magnitude(star.pos, satellite.pos)
    dir_star1 = normalize(sub(star.pos, satellite.pos))
    F1 = mul_s(dir_star1, (G * star.mass * satellite.mass) / (dist_star1**2))

    dist_sat1 = magnitude(satellite2.pos, satellite.pos)
    dir_sat1 = normalize(sub(satellite2.pos, satellite.pos))
    Fsat1 = mul_s(dir_sat1, (G * satellite2.mass * satellite.mass) / (dist_sat1**2))

    dist_star2 = magnitude(star.pos, satellite2.pos)
    dir_star2 = normalize(sub(star.pos, satellite2.pos))
    F2 = mul_s(dir_star2, (G * star.mass * satellite2.mass) / (dist_star2**2))

    dist_sat2 = magnitude(satellite.pos, satellite2.pos)
    dir_sat2 = normalize(sub(satellite.pos, satellite2.pos))
    Fsat2 = mul_s(dir_sat2, (G * satellite2.mass * satellite.mass) / (dist_sat2**2))

    Fg1 = add(F1, Fsat1)
    Fg2 = add(F2, Fsat2)

    satellite.acc = div_s(Fg1, satellite.mass)
    satellite.vel = add(satellite.vel, mul_s(satellite.acc, dt))
    satellite.pos = add(satellite.pos, mul_s(satellite.vel, dt))

    satellite2.acc = div_s(Fg2, satellite2.mass)
    satellite2.vel = add(satellite2.vel, mul_s(satellite2.acc, dt))
    satellite2.pos = add(satellite2.pos, mul_s(satellite2.vel, dt))




def prev_cals(bodies, dt):
    for b in bodies:
        b.forces = Vector(0, 0)

    for b1, b2 in itertools.combinations(bodies, 2):
        calcs3(b1, b2, dt)

    for b in bodies:
        b.acc = div_s(b.forces, b.mass)
        b.vel = add(b.vel, mul_s(b.acc, dt))
        b.pos = add(b.pos, mul_s(b.vel, dt))


def calcs3(body1, body2, dt):
    dist = magnitude(body1.pos, body2.pos)

    if dist == 0:
        return
        # exit()

    dir1 = normalize(sub(body2.pos, body1.pos))
    dir2 = normalize(sub(body1.pos, body2.pos))

    grav_mag = (G * body1.mass * body2.mass) / (dist**2)

    body1.forces = add(body1.forces, mul_s(dir1, grav_mag))
    body2.forces = add(body2.forces, mul_s(dir2, grav_mag))


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
    main()
