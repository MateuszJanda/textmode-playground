#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import collections as co
import sys
import time
import curses
import locale


BLANK_BRAILLE = u'\u2800'
CELL_WIDTH = 2
CELL_HEIGHT = 4

Point = co.namedtuple('Point', ['x', 'y'])


def main(scr):
    setup_curses()
    scr.clear()

    # num = 0
    while True:
        screen_buf = clear_screen()

        # draw_line(screen_buf, num)
        draw_line(screen_buf, Point(2, 5), Point(16, 8))
        # num += 1


        # if num > 40:
            # break

        refresh_screen(scr, screen_buf)
        time.sleep(0.1)

    time.sleep(2)
    curses.endwin()


def setup_curses():
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)


def draw():
    nx = ar.axis.x * math.cos(angel) - ar.axis.y * math.sin(angel)
    ny = ar.axis.x * math.sin(angel) + ar.axis.y * math.cos(angel)


def draw_line(screen_buf, pt1, pt2):
    # https://pl.wikipedia.org/wiki/Algorytm_Bresenhama
    x, y = pt1.x, pt1.y

    # Drawing direction
    if pt1.x < pt2.x:
        xi = 1
        dx = pt2.x - pt1.x
    else:
        xi = -1
        dx = pt1.x - pt2.x

    if (pt1.y < pt2.y):
        yi = 1
        dy = pt2.y - pt1.y
    else:
        yi = -1
        dy = pt1.y - pt2.y

    # First point
    draw_point(screen_buf, x, y)
    # Axis OX
    if dx > dy:
        ai = (dy - dx) * 2
        bi = dy * 2
        d = bi - dx
        while x != pt2.x:
            # coordinate test
            if d >= 0:
                x += xi
                y += yi
                d += ai
            else:
                d += bi
                x += xi
            draw_point(screen_buf, x, y)
    # Axis OY
    else:
        ai = (dx - dy) * 2
        bi = dx * 2
        d = bi - dy
        while y != pt2.y:
            # coordinate test
            if d >= 0:
                x += xi
                y += yi
                d += ai
            else:
                d += bi
                y += yi
            draw_point(screen_buf, x, y)

# def draw_line(screen_buf, num, f=lambda x:1*x+3):
#     for x in range(num):
#         y = f(x)
#         draw_point(screen_buf, x, y)


def draw_point(screen_buf, x, y):
    if curses.LINES - 1 - int(y/CELL_HEIGHT) < 0:
        return
    uchar = ord(screen_buf[curses.LINES - 1 - int(y/CELL_HEIGHT)][int(x/CELL_WIDTH)])
    screen_buf[curses.LINES - 1 - int(y/CELL_HEIGHT)][int(x/CELL_WIDTH)] = unicode_char(uchar | relative_uchar(y, x))


def unicode_char(param):
    if sys.version_info[0] == 2:
        return unichr(param)
    return chr(param)


def relative_uchar(y, x):
    bx = x % 2
    by = y % 4

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


def clear_screen():
    screen_buf = []
    for _ in range(curses.LINES):
        screen_buf.append((list(BLANK_BRAILLE * (curses.COLS - 1))))

    return screen_buf


def refresh_screen(scr, screen_buf):
    scr.clear()

    for num, line in enumerate(screen_buf):
        scr.addstr(num, 0, u''.join(line).encode('utf-8'))

    scr.refresh()


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
