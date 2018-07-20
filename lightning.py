#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import curses
import random
from time import sleep
import os
import subprocess
import collections
from threading import Thread


Light = collections.namedtuple('Light', ['y', 'x', 'symbol'])


def esetup():
    """ Hardcoded stderr console for debug prints.
    Console must exist before running script. """
    sys.stderr = open('/dev/pts/2', 'w')


def eprint(*args, **kwargs):
    """ Debug print function (on stderr) """
    print(*args, file=sys.stderr)


class LightningIndex:
    def __init__(self, index, branch):
        self.index = index
        self.branch = branch


def create_lightning():
    """ Create lightning - random path with branches """
    x = curses.COLS // 2 + random.randint(-10, 10)
    y = 0
    lightning = [Light(y, x, random.choice('/|\\'))]
    branches = []
    while y < curses.LINES - 1:
        _, _, prev_symbol = lightning[-1]
        if prev_symbol == '|':
            y += 1
            symbol = random.choice('/|\\')
        elif prev_symbol == '/':
            symbol = random.choice('/|\\_')
            if symbol == '/' or symbol == '_':
                x -= 1
            if symbol != '_':
                y += 1
        elif prev_symbol == '\\':
            symbol = random.choice('/|\\_')
            if symbol == '\\' or symbol == '_':
                x += 1
            if symbol != '_':
                y += 1
        elif prev_symbol == '_':
            if lightning[-1].x < lightning[-2].x:
                symbol = random.choice('/_')
                x -= 1
            else:
                symbol = random.choice('\\_')
                x += 1
            if symbol != '_':
                y += 1

        if random.randint(0, 30) == 1:
            branches.append(create_branch(lightning[-1], Light(y, x, symbol)))

        lightning.append(Light(y, x, symbol))

    return lightning, branches


def create_branch(prev, root):
    """ Create lightning branches. Similar like create_lightning """
    branch = [prev, root]
    y = root.y
    x = root.x
    for i in range(random.randint(15, 30)):
        _, _, prev_symbol = branch[-1]
        if prev_symbol == '|':
            y += 1
            symbol = random.choice('/\\')
        elif prev_symbol == '/':
            symbol = random.choice('/___')
            if symbol == '/' or symbol == '_':
                x -= 1
            if symbol != '_':
                y += 1
        elif prev_symbol == '\\':
            symbol = random.choice('\\___')
            if symbol == '\\' or symbol == '_':
                x += 1
            if symbol != '_':
                y += 1
        elif prev_symbol == '_':
            if branch[-1].x < branch[-2].x:
                symbol = random.choice('/___')
                x -= 1
            else:
                symbol = random.choice('\\___')
                x += 1
            if symbol != '_':
                y += 1

        if x < 0 or x >= curses.COLS or y < 0 or y >= curses.LINES:
            break
        branch.append(Light(y, x, symbol))

    del branch[0]
    return branch


def blink(scr, lightning, attr1, attr2):
    """ Blink main lightning branch on 0.1 seconds. Called when lightning hit ground. """
    for l in lightning:
        scr.addstr(l.y, l.x, l.symbol, attr1)

    sleep(0.1)
    scr.refresh()

    for l in lightning:
        scr.addstr(l.y, l.x, l.symbol, attr2)

    sleep(0.1)
    scr.refresh()


def indexer(light, branches):
    res = []
    for bs in branches:
        if light.x == bs[0].x and light.y == bs[0].y:
            res.append(LightningIndex(0, bs))

    return res

def setup_display():
    """ Setup display - don't know if it still needed, when using wrapper. """
    curses.start_color()        # Potrzebne do definiowania kolorów
    curses.use_default_colors() # Używaj kolorów terminala
    curses.halfdelay(5)         # Ile częśći sekundy czekamy na klawisz, od 1 do 255
    curses.noecho()             # Nie drukuje znaków na wejściu
    curses.curs_set(False)      # Wyłącza pokazywanie kursora


def colors():
    """ Setup lightning colors """
    gray = 2
    curses.init_color(1, 600, 600, 600)     # Zdefinuj kolor pod identyfikatorem 1,
                                            # daje kolor RGB, ale wartości 0-1000
    curses.init_pair(gray, 1, -1)           # Stwórz parę tło/czcionka. -1 przeźroczyste

    white = 3
    curses.init_pair(white, curses.COLOR_WHITE, -1)

    return gray, white


def check_exit_key(scr):
    ch = scr.getch()        # Oczekiwanie aż upłynie czas, lub albo zostanie
                            # naciśnięty klawisz
    return ch == ord('q')


def main(scr):
    # esetup()  # Just for debug
    setup_display()
    gray, white = colors()

    random.seed(4876)  # Just for debug

    while True:
        scr.clear()
        if check_exit_key(scr):
            break

        lightning, branches = create_lightning()
        indexed = [LightningIndex(0, lightning)]

        for l in lightning:
            indexed += indexer(l, branches)

            for i in indexed:
                if i.index >= len(i.branch):
                    continue

                light = i.branch[i.index]
                scr.addstr(light.y, light.x, light.symbol, curses.color_pair(gray))
                i.index += 1

            sleep(0.01)
            scr.refresh()

        blink(scr, lightning, curses.A_BOLD | curses.color_pair(white),
            curses.A_NORMAL | curses.color_pair(white))
        blink(scr, lightning, curses.A_BOLD | curses.color_pair(white),
            curses.A_NORMAL | curses.color_pair(white))

    curses.endwin()


if __name__ == '__main__':
    curses.wrapper(main)
