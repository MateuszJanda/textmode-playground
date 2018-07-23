#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import sys
import time
import curses
import locale


BLANK_BRAILLE = u'\u2800'


def main(scr):
    setup_curses()
    scr.clear()

    num = 0
    while True:
        screen_buf = []
        for _ in range(curses.LINES):
            screen_buf.append((list(BLANK_BRAILLE * (curses.COLS - 1))))

        draw_line(screen_buf, num)
        num += 1

        time.sleep(0.1)
        if num > 40:
            break

        show(scr, screen_buf)

    time.sleep(2)
    curses.endwin()


def setup_curses():
    curses.start_color()
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)


def draw_line(screen_buf, num, f=lambda x:1*x+3):
    for x in range(num):
        y = f(x)

        if curses.LINES - 1 - int(y / 4) < 0:
            continue
        uchar = ord(screen_buf[curses.LINES - 1 - int(y / 4)][int(x / 2)])
        screen_buf[curses.LINES - 1 - int(y / 4)][int(x / 2)] = unichr(uchar | relative_uchar(y, x))


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


def show(scr, screen_buf):
    scr.clear()

    for num, line in enumerate(screen_buf):
        scr.addstr(num, 0, u''.join(line).encode('utf-8'))

    scr.refresh()


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
