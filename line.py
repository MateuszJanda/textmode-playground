#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import math
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

    center_pt = Point(60, 50)
    pt1 = Point(60, 80)
    pt2 = Point(90, 50)
    pt3 = Point(60, 20)
    pt4 = Point(30, 50)
    angle = 0.1 / (2 * math.pi)

    while True:
        screen_buf = empty_screen_buf()

        pt1, pt2, pt3, pt4 = rotate_points(angle, center_pt, [pt1, pt2, pt3, pt4])
        draw_rect(screen_buf, pt1, pt2, pt3, pt4)

        refresh_screen(scr, screen_buf)
        time.sleep(0.02)

    time.sleep(2)
    curses.endwin()


def setup_curses():
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)


def rotate_points(angle, center_pt, points):
    result = []
    for pt in points:
        vec = Point(pt.x - center_pt.x, pt.y - center_pt.y)

        nx = vec.x * math.cos(angle) - vec.y * math.sin(angle)
        ny = vec.x * math.sin(angle) + vec.y * math.cos(angle)

        result.append(Point(center_pt.x + nx, center_pt.y + ny))

    return result


def draw_rect(screen_buf, pt1, pt2, pt3, pt4):
    for start, end in zip([pt1, pt2, pt3, pt4], [pt2, pt3, pt4, pt1]):
        start = Point(int(start.x), int(start.y))
        end = Point(int(end.x), int(end.y))
        draw_line(screen_buf, start, end)


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

    draw_point(screen_buf, Point(x, y))

    # X axis
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
            draw_point(screen_buf, Point(x, y))
    # Y axis
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
            draw_point(screen_buf, Point(x, y))


def draw_point(screen_buf, pt):
    if curses.LINES - 1 - int(pt.y/CELL_HEIGHT) < 0:
        return
    uchar = ord(screen_buf[curses.LINES - 1 - int(pt.y/CELL_HEIGHT)][int(pt.x/CELL_WIDTH)])
    screen_buf[curses.LINES - 1 - int(pt.y/CELL_HEIGHT)][int(pt.x/CELL_WIDTH)] = unicode_char(uchar | relative_uchar(pt.y, pt.x))


def unicode_char(param):
    if sys.version_info[0] == 2:
        return unichr(param)
    return chr(param)


def relative_uchar(y, x):
    bx = x % CELL_WIDTH
    by = y % CELL_HEIGHT

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


def empty_screen_buf():
    screen_buf = []
    for _ in range(curses.LINES):
        screen_buf.append((list(BLANK_BRAILLE * (curses.COLS - 1))))

    return screen_buf


def refresh_screen(scr, screen_buf):
    scr.clear()

    for num, line in enumerate(screen_buf):
        scr.addstr(num, 0, u''.join(line).encode('utf-8'))

    scr.refresh()


def setup_stderr():
    """Redirect stderr to other terminal. Run tty command, to get terminal id."""
    sys.stderr = open('/dev/pts/2', 'w')


def eprint(*args, **kwargs):
    """Print on stderr"""
    print(*args, file=sys.stderr)

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    setup_stderr()
    curses.wrapper(main)
