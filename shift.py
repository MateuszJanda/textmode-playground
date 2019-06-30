#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""


"""
       .__    .__  _____  __
  _____|  |__ |__|/ ____\/  |_
 /  ___/  |  \|  \   __\\   __\
 \___ \|   Y  \  ||  |   |  |
/____  >___|  /__||__|   |__|
     \/     \/
"""


import sys
import itertools as it
import curses
import locale
import numpy as np


EMPTY_BRAILLE = u'\u2800'
BLUE_RGB = (0, 247, 239)
RED_RGB  = (255, 0, 79)

HEIGHT = 4
WIDTH  = 2

BACKGROUND_ID = 1
BLUE_ID = 2
RED_ID  = 3


def main(scr):
    setup_stderr(terminal='/dev/pts/1')
    setup_curses(scr)

    arr = np.loadtxt('./shift.dot')

    assert arr.shape[0] % HEIGHT == 0
    assert arr.shape[1] % WIDTH == 0

    dots_arr = np.full(shape=(arr.shape[0] // HEIGHT, arr.shape[1] // WIDTH), fill_value=EMPTY_BRAILLE)

    for y, x in it.product(range(dots_arr.shape[0]), range(dots_arr.shape[1])):
        braille = create_braille(arr[y*HEIGHT:y*HEIGHT+HEIGHT, x*WIDTH:x*WIDTH+WIDTH])
        dots_arr[y, x] = braille

    draw(scr, dots_arr)
    while not is_exit_key(scr):
        pass


def setup_stderr(terminal='/dev/pts/1'):
    """
    Redirect stderr to other terminal. Run tty command, to get terminal id.

    $ tty
    /dev/pts/1
    """
    sys.stderr = open(terminal, 'w')


def setup_curses(scr):
    curses.use_default_colors()
    curses.start_color()
    curses.halfdelay(1)
    curses.curs_set(False)
    scr.clear()

    curses.init_color(1, *BLUE_RGB)
    curses.init_color(2, *RED_RGB)

    curses.init_pair(BACKGROUND_ID, curses.COLOR_WHITE, -1)
    curses.init_pair(BLUE_ID, 1, -1)
    curses.init_pair(RED_ID, 2, -1)


def log(*args, **kwargs):
    """log on stderr."""
    print(*args, file=sys.stderr)


def create_braille(arr):
    relative = 0
    for y, x in it.product(range(arr.shape[0]), range(arr.shape[1])):
        if arr[y, x] == 0:
            continue

        bx = x % WIDTH
        by = y % HEIGHT

        if bx == 0:
            if by == 3:
                relative |= 0x40
            else:
                relative |= 0x1 << by
        else:
            if by == 3:
                relative |= 0x80
            else:
                relative |= 0x8 << by

    return chr(ord(EMPTY_BRAILLE) | relative)


def draw(scr, arr):
    """Draw buffer content to screen."""
    dtype = np.dtype('U' + str(arr.shape[1]))
    for num, line in enumerate(arr):
        scr.addstr(num, 0, line.view(dtype)[0], curses.color_pair(BLUE_ID))
    scr.refresh()


def is_exit_key(scr):
    """Wait for key (defined by halfdelay), and check if q."""
    ch = scr.getch()
    return ch == ord('q')


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
