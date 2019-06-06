#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

import sys
import curses
import locale
import time
import math
import numpy as np


BODY_COUNT = 200
VIEWING_ANGLE = 120
MIN_DIST = 20
NEIGHB_RADIUS = 50
WEIGHT_VEL = 0.1
WEIGHT_NEIGHB_DIST = 0.15
WEIGHT_MIN_DIST = 0.15
WEIGHT_NOISE = 0.1
MAX_VEL = 4
DT = 1


class Body:
    def __init__(self, size):
        self.pos = np.array([np.random.uniform(0, size[0]),
                             np.random.uniform(0, size[1])])
        self.vel = np.random.uniform(-2, 2, size=[2])
        self.l = 1


def main(scr):
    setup_stderr()
    setup_curses()
    scr.clear()

    np.random.seed(3145)
    size = np.array([curses.LINES*4, (curses.COLS-1)*2])
    bodies = [Body(size) for _ in range(BODY_COUNT)]

    while True:
        for b1 in bodies:
            b1.avg_vel = np.copy(b1.vel)
            b1.avg_dist = 0
            b1.l = 1

            for b2 in bodies:
                if b1 is b2:
                    continue

                dist = math.sqrt((b1.pos[1] - b2.pos[1])**2 + (b1.pos[0] - b2.pos[0])**2)
                k = b1.vel[1] / math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) * \
                    ((b2.pos[1] - b1.pos[1]) / dist) + \
                    b1.vel[0] / math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) * \
                    ((b2.pos[0] - b1.pos[0]) / dist)

                if k < -1:
                    k = -1
                elif k > 0:
                    k = 1
                k = math.fabs(180*math.acos(k)) / math.pi
                if dist < NEIGHB_RADIUS and k > VIEWING_ANGLE:
                    b1.l += 1
                    b1.avg_vel += b2.vel
                    b1.avg_dist += dist

        for b1 in bodies:
            b1.vel += WEIGHT_VEL * ((b1.avg_vel / b1.l) - b1.vel)
            b1.vel += WEIGHT_NOISE * (np.random.uniform(0, 0.5, [2]) * MAX_VEL)
            if b1.l > 1:
                b1.avg_dist /= b1.l - 1

            for b2 in bodies:
                if b1 is b2:
                    continue

                dist = math.sqrt((b1.pos[1] - b2.pos[1])**2 + (b1.pos[0] - b2.pos[0])**2)
                k = b1.vel[1] / math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) * \
                    ((b2.pos[1] - b1.pos[1]) / dist) + \
                    b1.vel[0] / math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) * \
                    ((b2.pos[0] - b1.pos[0]) / dist)

                if k < -1:
                    k = -1
                elif k > 1:
                    k = 1
                k = math.fabs(180*math.acos(k)) / math.pi
                if dist < NEIGHB_RADIUS and k > VIEWING_ANGLE:
                    if math.fabs(b2.pos[1] - b1.pos[1]) > MIN_DIST:
                        b1.vel += (WEIGHT_NEIGHB_DIST / b1.l) * (((b2.pos - b1.pos) * (dist - b1.avg_dist)) / dist)
                    else:
                        b1.vel -= (WEIGHT_MIN_DIST / b1.l) * (((b2.pos - b1.pos) * MIN_DIST) / dist) - (b2.pos - b1.pos)

            if math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) > MAX_VEL:
                b1.vel = 0.75 * b1.vel

        for b in bodies:
            b.pos += b.vel * DT
            if b.vel[0] == 0:
                b.vel[0] = MAX_VEL / 1000
            if b.vel[1] == 0:
                b.vel[1] = MAX_VEL / 1000

        for b in bodies:
            if b.pos[1] < 0:
                b.pos[1] = b.pos[1] % -size[1] + size[1]
            elif b.pos[1] > size[1]:
                b.pos[1] = b.pos[1] % size[1]

            if b.pos[0] < 0:
                b.pos[0] = b.pos[0] % -size[0] + size[0]
            elif b.pos[0] > size[0]:
                b.pos[0] = b.pos[0] % size[0]

        draw(scr, bodies)

        # time.sleep(0.1)


def setup_curses():
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)


def setup_stderr():
    """Hard-coded console for debug prints (std err).
    Console must exist before running script."""
    sys.stderr = open('/dev/pts/1', 'w')


def eprint(*args, **kwargs):
    """Debug print function (on std err)"""
    print(*args, file=sys.stderr)


def draw(scr, bodies):
    # https://dboikliev.wordpress.com/2013/04/20/image-to-ascii-conversion/
    # http://mkweb.bcgsc.ca/asciiart/
    shape = [curses.LINES, curses.COLS - 1]
    count = np.full(shape=shape, fill_value=0)

    for b in bodies:
        if b.pos[0]//4 >= curses.LINES or b.pos[1]//2 >= curses.COLS - 1:
            continue
        count[int(b.pos[0]//4), int(b.pos[1]//2)] += 1

    TONE_SYMBOLS = '@%#x+=:-. '
    buf = np.full(shape=shape, fill_value=' ')
    for y in range(count.shape[0]):
        for x in range(count.shape[1]):
            if count[y][x] > 50:
                buf[y][x] = TONE_SYMBOLS[0]
            elif count[y][x] > 40:
                buf[y][x] = TONE_SYMBOLS[1]
            elif count[y][x] > 30:
                buf[y][x] = TONE_SYMBOLS[2]
            elif count[y][x] > 20:
                buf[y][x] = TONE_SYMBOLS[3]
            elif count[y][x] > 10:
                buf[y][x] = TONE_SYMBOLS[4]
            elif count[y][x] > 5:
                buf[y][x] = TONE_SYMBOLS[5]
            elif count[y][x] > 3:
                buf[y][x] = TONE_SYMBOLS[6]
            elif count[y][x] > 1:
                buf[y][x] = TONE_SYMBOLS[7]
            elif count[y][x] != 0:
                buf[y][x] = TONE_SYMBOLS[8]

    dtype = np.dtype('U' + str(buf.shape[1]))
    for num, line in enumerate(buf):
        scr.addstr(num, 0, line.view(dtype)[0])
    scr.refresh()

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
