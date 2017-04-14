#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import curses

def main():
    scr = setup()

    screen_buf = []
    for _ in range(curses.LINES):
        screen_buf.append(' ' * (curses.COLS - 1))

    print type(screen_buf)

    while True:
        ch = scr.getch()        # Oczekiwanie aż upłynie czas, lub albo zostanie
                                # naciśnięty klawisz
        if ch == ord('q'):
            break

        simulation(scr, screen_buf)

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

def simulation(scr, screen_buf):
    for num, line in enumerate(screen_buf):
        scr.addstr(num, 0, line)
        # scr.addstr(num, 0, 'asdf')

if __name__ == '__main__':
    main()