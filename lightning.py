#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam


import sys
import curses
import random
from time import sleep
import collections


GRAY = 2
WHITE = 3


LightPart = collections.namedtuple('LightPart', ['y', 'x', 'symbol'])


class Track:
    """ Keep tracking which part of lightning (root, branch) was drawn """
    def __init__(self, branch):
        self.branch_idx = 0
        self.branch = branch


def main(scr):
    # esetup()  # Just for debug
    setup_curses()
    setup_colors()

    random.seed(4876)

    while not check_exit_key(scr):
        scr.clear()

        root, branches = lightning()
        draw_lightning(scr, root, branches)

        blink(scr, root, curses.A_BOLD | curses.color_pair(WHITE),
            curses.A_NORMAL | curses.color_pair(WHITE))
        blink(scr, root, curses.A_BOLD | curses.color_pair(WHITE),
            curses.A_NORMAL | curses.color_pair(WHITE))


def esetup():
    """ Hard-coded console for debug prints (std err).
    Console must exist before running this script. """
    sys.stderr = open('/dev/pts/2', 'w')


def eprint(*args, **kwargs):
    """ Debug print function (on std err) """
    print(*args, file=sys.stderr)


def setup_curses():
    """ Setup curses """
    curses.start_color()         # Needed to define setup_colors
    curses.use_default_colors()  # Use terminal colors
    curses.halfdelay(1)          # Wait x tenths of seconds for key
    curses.curs_set(False)       # Disable cursor


def setup_colors():
    """ Setup colors """
    gray_fg = 1
    transparent_bg = -1

    # Define gray color under index 1 (RBG, value range [0, 1000])
    curses.init_color(gray_fg, 600, 600, 600)

    # Define pair (foreground, background) under index defined color "GRAY"
    curses.init_pair(GRAY, gray_fg, transparent_bg)
    curses.init_pair(WHITE, curses.COLOR_WHITE, transparent_bg)

    return GRAY, WHITE


def check_exit_key(scr):
    """ Wait for key (time defined by curses.halfdelay) """
    ch = scr.getch()
    return ch == ord('q')


def lightning():
    """ Create root lightning with random lightning branches """
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
    """ Create lightning branches. Similar to lightning """
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


def draw_lightning(scr, root, branches):
    """ Draw lightning building animation """
    tracks = [Track(root)]

    for l in root:
        tracks += add_starting_tracks(l, branches)
        draw_lightning_ends(scr, tracks)

        sleep(0.01)
        scr.refresh()


def add_starting_tracks(light_part, branches):
    """ Add all branches that start at given position """
    new_tracks = []
    for b in branches:
        if light_part.x == b[0].x and light_part.y == b[0].y:
            new_tracks.append(Track(b))

    return new_tracks


def draw_lightning_ends(scr, tracks):
    """ Draw lightning ends from all branches (stored in tracks list) """
    for t in tracks:
        if t.branch_idx >= len(t.branch):
            continue

        light_part = t.branch[t.branch_idx]
        t.branch_idx += 1
        scr.addstr(light_part.y, light_part.x, light_part.symbol, curses.color_pair(GRAY))


def blink(scr, lightning_root, attr1, attr2):
    """ Blink lightning on 0.1 seconds. Called when lightning hit ground. """
    for l in lightning_root:
        scr.addstr(l.y, l.x, l.symbol, attr1)

    sleep(0.1)
    scr.refresh()

    for l in lightning_root:
        scr.addstr(l.y, l.x, l.symbol, attr2)

    sleep(0.1)
    scr.refresh()


if __name__ == '__main__':
    curses.wrapper(main)
