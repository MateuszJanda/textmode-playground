#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from curses.textpad import Textbox, rectangle
import random
from time import sleep


def blink(lightning, attribute):
    for l in lightning:
        y, x, symbol = l
        stdscr.addstr(y, x, symbol, attribute)

    sleep(0.1)
    stdscr.refresh()


stdscr = curses.initscr()
curses.halfdelay(5)           # How many tenths of a second are waited, from 1 to 255
curses.noecho()               # Wont print the input
curses.curs_set(0)

# stdscr.addstr(0, 0, "Enter IM message: (hit Ctrl-G to send)")

# editwin = curses.newwin(5,30, 2,1)
# rectangle(stdscr, 1,0, 1+5+1, 1+30+1)
stdscr.refresh()


while True:
    char = stdscr.getch()        # This blocks (waits) until the time has elapsed,
                              # or there is input to be handled
    stdscr.clear()               # Clears the screen
    # if char != curses.ERR:    # This is true if the user pressed something
    #     stdscr.addstr(0, 0, chr(char))
    if char == ord('q'):
        break  # Exit the while loop
    elif char == curses.KEY_LEFT:
        break
    # else:
        # stdscr.addstr(0, 0, "Waiting")

    lightning = []
    x = curses.COLS / 2
    for y in range(0, curses.LINES):
        if len(lightning) > 0:
            _, _, lsymbol = lightning[-1]
            if lsymbol == '|':
                lightning.append((y, x, random.choice('//|\\\\')))
            elif lsymbol == '/':
                # x -= 1
                s = random.choice('//|\\\\')
                if s == '/':
                    x -= 1
                lightning.append((y, x, s))
            elif lsymbol == '\\':
                s = random.choice('//|\\\\')
                if s == '\\':
                    x += 1
                lightning.append((y, x, s))
            # if lsymbol = '_':
                # lightning.append((y, x+1, random.choice('/|\\_')))
            # pass
        else:
            lightning.append((y, x, random.choice('/|\\')))

        ly, lx, lsymbol = lightning[-1]
        stdscr.addstr(ly, lx, lsymbol)

        sleep(0.01)
        stdscr.refresh()

    blink(lightning, curses.A_BOLD)
    blink(lightning, curses.A_NORMAL)
    blink(lightning, curses.A_BOLD)
    blink(lightning, curses.A_NORMAL)

curses.endwin()