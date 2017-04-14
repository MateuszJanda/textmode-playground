#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import time
import curses
import locale

locale.setlocale(locale.LC_ALL, '')    # set your locale

def main():
    scr = setup()

    # screen_buf = []
    # for _ in range(curses.LINES):
    #     screen_buf.append((list(u'\u2800' * (curses.COLS - 1))))

    # draw_line(screen_buf)

    r = 0
    while True:

        screen_buf = []
        for _ in range(curses.LINES):
            screen_buf.append((list(u'\u2800' * (curses.COLS - 1))))

        draw_line(screen_buf, r)
        r += 1

        time.sleep(0.001)

        if r > 40:
            break


        display(scr, screen_buf)

    time.sleep(2)
    curses.endwin()             # Przywraca terminal do oryginalnych ustawień


def setup():
    scr = curses.initscr()
    curses.start_color()        # Potrzebne do definiowania kolorów
    curses.use_default_colors() # Używaj kolorów terminala
    curses.halfdelay(5)         # Ile częśći sekundy czekamy na klawisz, od 1 do 255
    curses.noecho()             # Nie drukuje znaków na wejściu
    curses.curs_set(False)      # Wyłącza pokazywanie kursora
    scr.clear()

    return scr


def draw_line(screen_buf, rrr):
    """ y = 6x + 3, x w [0, 40]"""

    # x < curses.COLS * 2
    for x in range(rrr):
        y = 1 * x + 3

        if curses.LINES - 1 - int(y / 4) < 0:
            continue
        # screen_buf[int(y / 4)][int(x / 2)] = u'x'
        uchar = ord(screen_buf[curses.LINES - 1 - int(y / 4)][int(x / 2)])
        screen_buf[curses.LINES - 1 - int(y / 4)][int(x / 2)] = unichr(uchar | fun(y, x))



def fun(y, x):
    bx = x % 2
    by = y % 4

    if bx == 0:
        if by == 0:
            return 0x40
        else:
            return 0x4 >> (by - 1)
    else:
        if by == 0:
            return 0x80
        else:
            return 0x20 >> (by -1)


def display(scr, screen_buf):
    scr.clear()

    for num, line in enumerate(screen_buf):
        scr.addstr(num, 0, u''.join(line).encode('utf-8'))
        # scr.addstr(num, 0, 'asdf')n)

    scr.refresh()


if __name__ == '__main__':
    main()

