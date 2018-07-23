#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
|     .-.
|    /   \         .-.
|   /     \       /   \       .-.     .-.     _   _
+--/-------\-----/-----\-----/---\---/---\---/-\-/-\/\/---
| /         \   /       \   /     '-'     '-'
|/           '-'         '-'

unknown
"""

import curses
import math
import random
from time import sleep
import locale


BLANK_BRAILLE = u'\u2800'


def main(scr):
    setup_curses()
    scr.clear()

    buf = clean_buf()
    x = 0

    while not check_exit_key(scr):
        shift_buf(buf)
        draw_pt(buf, x)
        show(buf)

        x += 1
        sleep(0.1)
        scr.refresh()


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


def shift_buf(buf):
    pass


def draw_pt(buf, x, f=lambda x: 3*math.sin(x*3)):
    pass


def show(buf):
    pass


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    # locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    curses.wrapper(main)

