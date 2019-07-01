#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""


import sys
import itertools as it
import curses
import locale
import random
import time
import numpy as np


def rgb(r, g, b):
    return (r*1000)//255, (g*1000)//255, (b*1000)//255


EMPTY_BRAILLE = u'\u2800'

BLACK_RGB = rgb(0, 0, 0)
WHITE_RGB = rgb(255, 255, 255)
BLUE_RGB = rgb(0, 247, 239)
RED_RGB = rgb(255, 0, 79)

WHITE_ID = 1
BLUE_ID = 2
RED_ID = 3
BACKGROUND_ID = 4

HEIGHT = 4
WIDTH = 2

SHIFT =  r"""
       .__    .__  _____  __
  _____|  |__ |__|/ ____\/  |_
 /  ___/  |  \|  \   __\\   __\
 \___ \|   Y  \  ||  |   |  |
/____  >___|  /__||__|   |__|
     \/     \/
"""


def main(scr):
    setup_stderr(terminal='/dev/pts/1')
    setup_curses(scr)

    orig_arr = np.loadtxt('./shift.dot')

    assert orig_arr.shape[0] % HEIGHT == 0
    assert orig_arr.shape[1] % WIDTH == 0

    while True:
        scr.clear()

        shift_x, shift_y = random.choice(range(-2, 2)), random.choice(range(-2, 2))
        arr1 = create_shift_arr(orig_arr, shift_x, shift_y)
        shift_x, shift_y = random.choice(range(-2, 2)), random.choice(range(-2, 2))
        arr2 = create_shift_arr(arr1, shift_x, shift_y)
        shift_x, shift_y = random.choice(range(-2, 2)), random.choice(range(-2, 2))
        arr3 = create_shift_arr(orig_arr, shift_x, shift_y)

        dots_arr1 = create_dots_arr(arr1)
        dots_arr2 = create_dots_arr(arr2)
        dots_arr3 = create_dots_arr(arr3)

        call_data = [
            (dots_arr1, WHITE_ID),
            (dots_arr2, RED_ID),
            (dots_arr3, BLUE_ID)
        ]

        random.shuffle(call_data)
        for arr, color in call_data:
            draw(scr, arr, curses.color_pair(color))

        _, color = random.choice(call_data)
        draw_ascii_shift(scr, color)

        time.sleep(0.01)
        scr.refresh()

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
    curses.start_color()
    curses.halfdelay(1)
    curses.curs_set(False)

    curses.init_color(0, *BLACK_RGB)
    curses.init_color(1, *WHITE_RGB)
    curses.init_color(2, *BLUE_RGB)
    curses.init_color(3, *RED_RGB)

    curses.init_pair(WHITE_ID, 1, 0)
    curses.init_pair(BLUE_ID, 2, 0)
    curses.init_pair(RED_ID, 3, 0)
    curses.init_pair(BACKGROUND_ID, 0, 0)

    scr.bkgd(' ', curses.color_pair(BACKGROUND_ID))
    scr.clear()


def log(*args, **kwargs):
    """log on stderr."""
    print(*args, file=sys.stderr)


def create_shift_arr(orig_arr, shift_x, shift_y):
    new_arr = np.copy(orig_arr)

    if shift_x:
        wall_x = np.full(shape=(new_arr.shape[0], abs(shift_x)), fill_value=0)
        if shift_x > 0:
            new_arr = np.concatenate((wall_x, new_arr), axis=1)
            new_arr = np.delete(new_arr, np.s_[new_arr.shape[1]-shift_x:], axis=1)
        else:
            new_arr = np.concatenate((new_arr, wall_x), axis=1)
            new_arr = np.delete(new_arr, np.s_[:-shift_x], axis=1)

    if shift_y:
        wall_y = np.full(shape=(abs(shift_y), new_arr.shape[1]), fill_value=0)
        if shift_y > 0:
            new_arr = np.concatenate((wall_y, new_arr), axis=0)
            new_arr = np.delete(new_arr, np.s_[new_arr.shape[0]-shift_y:], axis=0)
        else:
            new_arr = np.concatenate((new_arr, wall_y), axis=0)
            new_arr = np.delete(new_arr, np.s_[:-shift_y], axis=0)

    return new_arr


def create_dots_arr(arr):
    dots_arr = np.full(shape=(arr.shape[0] // HEIGHT, arr.shape[1] // WIDTH), fill_value=EMPTY_BRAILLE)

    for y, x in it.product(range(dots_arr.shape[0]), range(dots_arr.shape[1])):
        braille = create_braille(arr[y*HEIGHT:y*HEIGHT+HEIGHT, x*WIDTH:x*WIDTH+WIDTH])
        dots_arr[y, x] = braille

    return dots_arr


def create_braille(arr):
    """Create braille character from 8x4 array."""
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


def draw_ascii_shift(scr, color):
    Y_SHIFT = 9
    for y, text in enumerate(SHIFT.split('\n')):
        scr.addstr(y + Y_SHIFT, 0, text, curses.color_pair(color))


def is_exit_key(scr):
    """Wait for key (defined by halfdelay), and check if q."""
    ch = scr.getch()
    return ch == ord('q')


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
