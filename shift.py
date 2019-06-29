#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

import sys
import curses
import numpy as np


def main(scr):
    setup_stderr(terminal='/dev/pts/1')
    setup_curses(scr)


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


if __name__ == '__main__':
    curses.wrapper(main)
