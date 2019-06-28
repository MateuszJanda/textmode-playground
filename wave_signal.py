#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

import sys
import curses
import time
import locale


BLANK_BRAILLE = u'\u2800'
WAVE = '''`-._,-'"'''


def main(scr):
    setup_curses(scr)

    step = 0
    while True:
        simple_wave(scr, step, length=10)

        step += 1
        scr.refresh()
        time.sleep(0.1)


def setup_curses(scr):
    curses.use_default_colors()
    curses.halfdelay(1)
    curses.curs_set(False)
    scr.clear()


def setup_stderr(terminal='/dev/pts/1'):
    """
    Redirect stderr to other terminal. Run tty command, to get terminal id.

    $ tty
    /dev/pts/1
    """
    sys.stderr = open(terminal, 'w')


def log(*args, **kwargs):
    """log on stderr."""
    print(*args, file=sys.stderr)


def is_exit_key(scr):
    """Wait for key (defined by halfdelay), and check if q."""
    ch = scr.getch()
    return ch == ord('q')


def simple_wave(scr, step, length=len(WAVE)):
    # Length which fully contains user wave
    basic_length = length // len(WAVE) + 1
    # One extra wave for shifting
    wave = WAVE * (basic_length + 1)

    shift = step % len(WAVE)
    wave = '[' + wave[shift:shift+length] + ']'

    scr.addstr(0, 0, wave)


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
