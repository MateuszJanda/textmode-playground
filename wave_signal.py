#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from curses.textpad import Textbox, rectangle
import random
from time import sleep
import locale


"""
|     .-.
|    /   \         .-.
|   /     \       /   \       .-.     .-.     _   _
+--/-------\-----/-----\-----/---\---/---\---/-\-/-\/\/---
| /         \   /       \   /     '-'     '-'
|/           '-'         '-'

unknown
"""


stdscr = curses.initscr()
curses.halfdelay(5)           # How many tenths of a second are waited, from 1 to 255
curses.noecho()               # Wont print the input
curses.curs_set(0)

stdscr.clear()
stdscr.refresh()

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

i = 0x2800
while True:
    char = stdscr.getch()        # This blocks (waits) until the time has elapsed,
                              # or there is input to be handled

    if char == ord('q'):
        break
    elif char == curses.KEY_LEFT:
        break

    # s = u''.join(wave)
    # s = ' '.join(wave)
    # stdscr.addstr(2, 10, s.encode('utf-8'))
    # stdscr.addstr(2, 10, u'\u2833'.encode('utf-8'))
    # stdscr.addstr(2, 10, s)
    # stdscr.addstr(2, 10, unichr(i).encode('utf-8'))
    stdscr.addch(ord(u'\u2833'))
    # print unichr(i).encode('utf-8')
    i += 1
    sleep(0.1)
    stdscr.refresh()

    continue
    wave = wave[1:]
    wave.append(unichr(0x2800 + random.randint(0, 0xff)))

curses.endwin()