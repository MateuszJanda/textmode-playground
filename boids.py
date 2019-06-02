#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

import curses
import locale


BODY_COUNT = 25
NEIGHBORHOOD_RADIUS = 3
VIEWING_ANGLE = 20
MIN_DISTANCE = 20




class Body:
    def __init__(self, pos, vel):
        self.pos = pos
        self.vel = vel


def main():
    setup_curses()

    bodis = []
    for i in range(BODY_COUNT):
        bodis.append(Body(pos=(0, 0), vel=(0, 0)))





def setup_curses():
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)




if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)

