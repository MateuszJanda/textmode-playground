#!/usr/bin/env python

"""
|     .-.
|    /   \         .-.
|   /     \       /   \       .-.     .-.     _   _
+--/-------\-----/-----\-----/---\---/---\---/-\-/-\/\/---
| /         \   /       \   /     '-'     '-'
|/           '-'         '-'

unknown
"""

import sys
import curses
import math
import random
from time import sleep
import collections
import locale


BLANK_BRAILLE = u'\u2800'

Point = collections.namedtuple('Point', ['x', 'y'])


def main(scr):
    setup_curses()
    scr.clear()

    screen_buf = clean_buf()
    x = 0

    while not check_exit_key(scr):
        shift_buf(screen_buf)
        draw_amp(screen_buf, x)
        show(scr, screen_buf)

        x += 1
        sleep(0.1)


def setup_curses():
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)


def clean_buf():
    return [list(BLANK_BRAILLE * (curses.COLS - 1)) for _ in range(curses.LINES)]


def check_exit_key(scr):
    """ Wait for key (defined by halfdelay), and check if q """
    ch = scr.getch()
    return ch == ord('q')


def shift_buf(screen_buf):
    pass


def draw_amp(screen_buf, x, f=lambda x: 3*math.sin(x*3)):
    ox = 25
    last_x = len(screen_buf[0][0]) * 2

    for y in range(int(f(x))):
        draw_pt(screen_buf, Point(last_x, -y + ox))


def draw_pt(screen_buf, pt):
    x = int(pt.x / 2)
    y = curses.LINES - 1 - int(pt.y / 4)

    if pt.y < 0 or y < 0 or pt.x < 0 or x >= curses.COLS - 1:
        return

    uchar = ord(screen_buf[y][x])
    screen_buf[y][x] = unicode_char(uchar | relative_uchar(pt))


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


def unicode_char(param):
    if sys.version_info[0] == 2:
        return unichr(param)
    return chr(param)


def show(scr, screen_buf):
    for num, line in enumerate(screen_buf):
        scr.addstr(num, 0, u''.join(line).encode('utf-8'))

    scr.refresh()


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    # locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    curses.wrapper(main)

