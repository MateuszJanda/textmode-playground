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

WHITE_ID = 1
BLUE_ID = 2
RED_ID  = 3


def main(scr):
    setup_stderr(terminal='/dev/pts/1')
    setup_curses(scr)

    arr1 = np.loadtxt('./shift.dot')
    arr2 = np.copy(arr1)

    assert arr1.shape[0] % HEIGHT == 0
    assert arr1.shape[1] % WIDTH == 0

    shift = np.full(shape=(arr2.shape[0], 2), fill_value=0)
    arr2 = np.concatenate((shift, arr2), axis=1)
    arr2 = np.delete(arr2, -2, axis=1)

    dots_arr1 = create_dots_arr(arr1)
    dots_arr2 = create_dots_arr(arr2)

    draw(scr, dots_arr1, curses.color_pair(WHITE_ID))
    draw(scr, dots_arr2, curses.color_pair(BLUE_ID))

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

    curses.init_pair(WHITE_ID, curses.COLOR_WHITE, -1)
    curses.init_pair(BLUE_ID, 1, -1)
    curses.init_pair(RED_ID, 2, -1)


def log(*args, **kwargs):
    """log on stderr."""
    print(*args, file=sys.stderr)


def create_dots_arr(arr):
    dots_arr = np.full(shape=(arr.shape[0] // HEIGHT, arr.shape[1] // WIDTH), fill_value=EMPTY_BRAILLE)

    for y, x in it.product(range(dots_arr.shape[0]), range(dots_arr.shape[1])):
        braille = create_braille(arr[y*HEIGHT:y*HEIGHT+HEIGHT, x*WIDTH:x*WIDTH+WIDTH])
        dots_arr[y, x] = braille

    return dots_arr


def create_braille(arr):
    relative = 0
    for y, x in np.argwhere(arr != 0):
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


def draw(scr, arr, color):
    """Draw buffer content to screen."""
    for y, x in np.argwhere(arr != EMPTY_BRAILLE):
        scr.addstr(y, x, arr[y, x], color)
    scr.refresh()


def is_exit_key(scr):
    """Wait for key (defined by halfdelay), and check if q."""
    ch = scr.getch()
    return ch == ord('q')


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
