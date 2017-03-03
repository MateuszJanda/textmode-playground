#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from curses.textpad import Textbox, rectangle
import random
from time import sleep
import collections

Light = collections.namedtuple('Light', ['y', 'x', 'symbol'])


class LightningIndex:
    def __init__(self, index, branch):
        self.index = index
        self.branch = branch


def createLightning():
    x = curses.COLS / 2 + random.randint(-10, 10)
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
            branches.append(createBranch(lightning[-1], Light(y, x, symbol)))

        lightning.append(Light(y, x, symbol))

    return lightning, branches


def createBranch(prev, root):
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


def blink(lightning, attr1, attr2):
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


scr = curses.initscr()
curses.start_color()
curses.use_default_colors()
curses.halfdelay(5)       # How many tenths of a second are waited, from 1 to 255
curses.noecho()           # Wont print the input
curses.curs_set(False)
random.seed(4876)

GRAY = 2
curses.init_color(1, 600, 600, 600)
curses.init_pair(2, 1, -1)

WHITE = 3
curses.init_pair(3, curses.COLOR_WHITE, -1)


while True:
    # This blocks (waits) until the time has elapsed, or there is input to be handled
    char = scr.getch()
    scr.clear()

    if char == ord('q'):
        break

    lightning, branches = createLightning()
    indexed = [LightningIndex(0, lightning)]

    for l in lightning:
        indexed += indexer(l, branches)

        for i in indexed:
            if i.index >= len(i.branch):
                continue

            light = i.branch[i.index]
            scr.addstr(light.y, light.x, light.symbol, curses.color_pair(GRAY))
            i.index += 1

        sleep(0.01)
        scr.refresh()

    scr.refresh()

    blink(lightning, curses.A_BOLD | curses.color_pair(WHITE),
        curses.A_NORMAL | curses.color_pair(WHITE))
    blink(lightning, curses.A_BOLD | curses.color_pair(WHITE),
        curses.A_NORMAL | curses.color_pair(WHITE))

curses.endwin()
