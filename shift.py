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


def main(scr):
    setup_stderr(terminal='/dev/pts/1')
    setup_curses(scr)

    arr = np.loadtxt('./shift.dot')

    assert arr.shape[0] % 4 == 0
    assert arr.shape[1] % 2 == 0

    dots_arr = np.full(shape=(arr.shape[0] // 4, arr.shape[1] // 2), fill_value=EMPTY_BRAILLE)

    for y, x in it.product(range(dots_arr.shape[0]), range(dots_arr.shape[1])):
        braille = create_braille(arr[y*4:y*4+4, x*2:x*2+2])
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
    curses.halfdelay(1)
    curses.curs_set(False)
    scr.clear()


def log(*args, **kwargs):
    """log on stderr."""
    print(*args, file=sys.stderr)


def create_braille(arr):
    relative = 0
    for y, x in it.product(range(arr.shape[0]), range(arr.shape[1])):
        bx = x % 2
        by = y % 4

        if bx == 0:
            if by == 0:
                relative |= 0x40
            else:
                relative |= 0x4 >> (by - 1)
        else:
            if by == 0:
                relative |= 0x80
            else:
                relative |= 0x20 >> (by -1)

    return chr(ord(EMPTY_BRAILLE) | relative)


def draw(scr, arr):
    """Draw buffer content to screen."""
    dtype = np.dtype('U' + str(arr.shape[1]))
    for num, line in enumerate(arr):
        scr.addstr(num, 0, line.view(dtype)[0])
    scr.refresh()


def is_exit_key(scr):
    """Wait for key (defined by halfdelay), and check if q."""
    ch = scr.getch()
    return ch == ord('q')


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)

