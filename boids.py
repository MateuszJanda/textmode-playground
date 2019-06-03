#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

import curses
import locale
import time
import numpy as np


BODY_COUNT = 25
VIEWING_ANGLE = 20
MIN_DISTANCE = 20
NEIGHBORHOOD_RADIUS = 3
NEIGHBORHOOD_VEL_WEIGHT = 0.1
NEIGHBORHOOD_DIST_WEIGHT = 0.15
MIN_DIST_WEIGHT = 0.15
NOISE_WEIGHT = 0.1
MAX_VEL = 4


class Body:
    def __init__(self):
        self.pos = np.random.randint(0, 400, [2, 1])
        self.vel = np.random.randint(0, 2, [2, 1])


def main():
    setup_curses()

    bodies = []
    for i in range(BODY_COUNT):
        bodis.append(Body())

    while True:
        draw(bodies)

        for b1 in bodies:
            b1.avg_vel = b.vel
            b1.avg_dist = 0

            for b2 in bodies:
                if b1 is b2:
                    continue

                dist = math.sqrt((b1.pos[0] - b2.pos[0])**2 + (b1.pos[1] - b2.pos[1])**2)
                k = b1.vel[0] / math.sqrt(b1.vel[0]*b1.vel[0] + b1.vel[1]*b1.vel[1]) *
                    ((b2.x - b1.x) / dist) +
                    b1.vel[1] / math.sqrt(b1.vel[0]*b1.vel[0] + b1.vel[1]*b1.vel[1]) *
                    ((b2.y - b1.y) / dist)


        time.sleep(0.2)



def setup_curses():
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)



def draw(bodies):
    pass



if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)

