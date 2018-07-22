#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import curses
import random
from time import sleep
import collections


LightPart = collections.namedtuple('LightPart', ['y', 'x', 'symbol'])


def esetup():
    """ Hard-coded std err console for debug prints.
    Console must exist before running script. """
    sys.stderr = open('/dev/pts/2', 'w')


def eprint(*args, **kwargs):
    """ Debug print function (on std err) """
    print(*args, file=sys.stderr)


class LightningIndex:
    def __init__(self, branch):
        self.index = 0
        self.branch = branch


def lightning():
    """ Create main lightning with random lightning branches """
    x = curses.COLS // 2 + random.randint(-10, 10)
    y = 0
    root = [LightPart(y, x, random.choice('/|\\'))]
    branches = []
    while y < curses.LINES - 1:
        _, _, prev_symbol = root[-1]
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
            if root[-1].x < root[-2].x:
                symbol = random.choice('/_')
                x -= 1
            else:
                symbol = random.choice('\\_')
                x += 1
            if symbol != '_':
                y += 1

        if random.randint(0, 30) == 1:
            branches.append(lightning_branch(root[-1], LightPart(y, x, symbol)))

        root.append(LightPart(y, x, symbol))

    return root, branches


def lightning_branch(prev, root):
    """ Create lightning branches. Similar like lightning """
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
        branch.append(LightPart(y, x, symbol))

    del branch[0]
    return branch


def blink(scr, lightning, attr1, attr2):
    """ Blink lightning on 0.1 seconds. Called when lightning hit ground. """
    for l in lightning:
        scr.addstr(l.y, l.x, l.symbol, attr1)

    sleep(0.1)
    scr.refresh()

    for l in lightning:
        scr.addstr(l.y, l.x, l.symbol, attr2)

    sleep(0.1)
    scr.refresh()


def indexer(light_part, branches):
    result = []
    for b in branches:
        if light_part.x == b[0].x and light_part.y == b[0].y:
            result.append(LightningIndex(b))

    return result


def setup_curses():
    """ Setup curses """
    curses.start_color()        # Needed to define colors
    curses.use_default_colors() # Use terminal colors
    curses.halfdelay(1)         # Wait x tenths of seconds for key
    curses.curs_set(False)      # Disable cursor


def colors():
    """ Lightning colors """
    # Define gray color under index 1 (RBG, value rane [0, 1000])
    curses.init_color(1, 600, 600, 600)
    # Define pair under index 2
    gray = 2
    curses.init_pair(gray, 1, -1)           # Stwórz parę tło/czcionka. -1 przeźroczyste

    white = 3
    curses.init_pair(white, curses.COLOR_WHITE, -1)

    return gray, white


def check_exit_key(scr):
    # Wait for key (time defined by halfdelay)
    ch = scr.getch()
    return ch == ord('q')


def main(scr):
    # esetup()  # Just for debug
    setup_curses()
    gray, white = colors()

    random.seed(4876)  # Just for debug

    while not check_exit_key(scr):
        scr.clear()

        lightning_root, lightning_branches = lightning()
        indexed = [LightningIndex(lightning_root)]

        for l in lightning_root:
            indexed += indexer(l, lightning_branches)

            for i in indexed:
                if i.index >= len(i.branch):
                    continue

                light = i.branch[i.index]
                scr.addstr(light.y, light.x, light.symbol, curses.color_pair(gray))
                i.index += 1

            sleep(0.01)
            scr.refresh()

        blink(scr, lightning_root, curses.A_BOLD | curses.color_pair(white),
            curses.A_NORMAL | curses.color_pair(white))
        blink(scr, lightning_root, curses.A_BOLD | curses.color_pair(white),
            curses.A_NORMAL | curses.color_pair(white))


if __name__ == '__main__':
    curses.wrapper(main)
