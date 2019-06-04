#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

import curses
import locale
import time
import math
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
        self.pos = np.random.uniform(0, 400, [2, 1])
        self.vel = np.random.uniform(0, 2, [2, 1])
        self.l = 0


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

                dist = math.sqrt((b1.pos[1] - b2.pos[1])**2 + (b1.pos[0] - b2.pos[0])**2)
                k = b1.vel[1] / math.sqrt(b1.vel[1]**2 + b1.pos[0]**2) *
                    ((b2.pos[1] - b1.pos[1]) / dist) +
                    b1.pos[0] / math.sqrt(b1.vel[1]**2 + b1.pos[0]**2) *
                    ((b2.pos[0] - b1.pos[0]) / dist)
                if k < -1:
                    k = -1
                elif k > 0:
                    k = 1
                k = math.fabs(180*math.acos(k)) / maht.pi
                if dist < NEIGHBORHOOD_RADIUS and k > VIEWING_ANGLE:
                    b1.l += 1
                    b1.avg_vel += b2.vel
                    b1.avg_dist += dist

        for b1 in bodies:
            b1.vel += NEIGHBORHOOD_VEL_WEIGHT * ((b1.avg_vel / b1.l) - b1.vel)
            b1.vel += NOISE_WEIGHT * (np.random.uniform(0, 0.5, [2, 1]) * MAX_VEL)
            if b1.l > 1:
                b1.avg_dist /= b1.l - 1

            for b2 in bodies:
                if b1 is b2:
                    continue

                dist = math.sqrt((b1.pos[1] - b2.pos[1])**2 + (b1.pos[0] - b2.pos[0])**2)
                k = b1.vel[1] / math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) *
                    ((b2.pos[1] -b1.pos[1]) / dist) +
                    b1.vel[0] / math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) *
                    ((b2.pos[0] - b1.pos[0]) / dist)

                if k < -1:
                    k = -1
                elif k > 1:
                    k = 1
                k = math.fabs(180*math.acos(k)) / maht.pi
                if dist < NEIGHBORHOOD_RADIUS and k > VIEWING_ANGLE:
                    if math.fabs(b2.pos[1] - b1.pos[1]) > MIN_DISTANCE:
                        b1.vel += (NEIGHBORHOOD_DIST_WEIGHT / b1.l) * (((b2.pos - b1.pos) * (dist - b1.avg_dist)) / dist)

                    else:
                        b1.vel += (MIN_DIST_WEIGHT / b1.l) * (((b2.pos - b1.pos) * MIN_DISTANCE) / dist) - (b2.pos - b1.pos)


            if math.sqrt(b1.vel[1]**2 + b1.vel[0]**2) > MAX_VEL:
                b1.vel = 0.75 * b1.vel

        for b in bodies:
            if b1.vel[1] < 0:
                b1.vel[1] += 450
            if b1.vel[0] < 0:
                b1.vel[0] += 400
            if b1.vel[1] > 450:
                b1.vel[1] -= 450
            if v1.vel[0] > 400:
                b1.vel[0] -= 400


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

