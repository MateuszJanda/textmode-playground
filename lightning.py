#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from curses.textpad import Textbox, rectangle
import random
from time import sleep


def blink(lightning, attr1, attr2):
    for l in lightning:
        y, x, symbol = l
        stdscr.addstr(y, x, symbol, attr1)

    sleep(0.1)
    stdscr.refresh()

    for l in lightning:
        y, x, symbol = l
        stdscr.addstr(y, x, symbol, attr2)

    sleep(0.1)
    stdscr.refresh()


def createNewSymbol(prev):
    if prev == '|':
        return random.choice('/|\\')
    if prev == '_':
        return random.choice('/\\_')
    return random.choice('/|\\_')


stdscr = curses.initscr()
curses.halfdelay(5)           # How many tenths of a second are waited, from 1 to 255
curses.noecho()               # Wont print the input
curses.curs_set(0)

stdscr.refresh()


while True:
    # This blocks (waits) until the time has elapsed, or there is input to be handled
    char = stdscr.getch()
    stdscr.clear()

    if char == ord('q'):
        break

    lightning = []
    x = curses.COLS / 2 + random.randint(-10, 10)
    y = 0
    while y < curses.LINES - 1:
        if not lightning:
            lightning.append((y, x, random.choice('/|\\')))
        else:
            _, _, prev_symbol = lightning[-1]
            if prev_symbol == '|':
                y += 1
                lightning.append((y, x, createNewSymbol(prev_symbol)))
            elif prev_symbol == '/':
                symbol = createNewSymbol(prev_symbol)
                if symbol == '/' or symbol == '_':
                    x -= 1
                if symbol != '_':
                    y += 1
                lightning.append((y, x, symbol))
            elif prev_symbol == '\\':
                symbol = createNewSymbol(prev_symbol)
                if symbol == '\\' or symbol == '_':
                    x += 1
                if symbol != '_':
                    y += 1
                lightning.append((y, x, symbol))
            elif prev_symbol == '_':
                if lightning[-1][1] < lightning[-2][1]:
                    symbol = random.choice('/_')
                    x -= 1
                else:
                    symbol = random.choice('\\_')
                    x += 1
                if symbol != '_':
                    y += 1
                lightning.append((y, x, symbol))

        ly, lx, lsymbol = lightning[-1]
        try:
            stdscr.addstr(ly, lx, lsymbol)
        except:
            print ly, lx, curses.LINES, lsymbol

        # sleep(0.01)
        stdscr.refresh()

    blink(lightning, curses.A_BOLD, curses.A_NORMAL)
    blink(lightning, curses.A_BOLD, curses.A_NORMAL)

curses.endwin()
