#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
import random
from time import sleep
import os
import subprocess
import collections
from threading import Thread


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


def thunderSound():
    FNULL = open(os.devnull, 'w')
    subprocess.call(['ffplay', '-nodisp', '-autoexit', 'thunder.mp3'],
        stdout=FNULL, stderr=subprocess.STDOUT)


def main(scr):
    curses.start_color()        # Potrzebne do definiowania kolorów
    curses.use_default_colors() # Używaj kolorów terminala
    curses.halfdelay(5)         # Ile częśći sekundy czekamy na klawisz, od 1 do 255
    curses.noecho()             # Nie drukuje znaków na wejściu
    curses.curs_set(False)      # Wyłącza pokazywanie kursora

    GRAY = 2
    curses.init_color(1, 600, 600, 600)     # Zdefinuj kolor pod identyfikatorem 1,
                                            # daje kolor RGB, ale wartości 0-1000
    curses.init_pair(GRAY, 1, -1)           # Stwórz parę tło/czcionka. -1 przeźroczyste

    WHITE = 3
    curses.init_pair(WHITE, curses.COLOR_WHITE, -1)

    random.seed(4876)
    th = Thread(target=thunderSound)

    while True:
        ch = scr.getch()        # Oczekiwanie aż upłynie czas, lub albo zostanie
                                # naciśnięty klawisz
        scr.clear()             # Czyści ekran

        if ch == ord('q'):
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
            scr.refresh()       # Odświeżanie ekranu

        th.start()

        blink(lightning, curses.A_BOLD | curses.color_pair(WHITE),
            curses.A_NORMAL | curses.color_pair(WHITE))
        blink(lightning, curses.A_BOLD | curses.color_pair(WHITE),
            curses.A_NORMAL | curses.color_pair(WHITE))

        break

    th.join()
    curses.endwin()             # Przywraca terminal do oryginalnych ustawień


if __name__ == '__main__':
    curses.wrapper(main)
