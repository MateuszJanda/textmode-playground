#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import math
import time
import curses
import locale

locale.setlocale(locale.LC_ALL, '')    # set your locale

class Body:
    pass


class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y


G = 1.0


def main():
    scr = setup()

    # screen_buf = []
    # for _ in range(curses.LINES):
    #     screen_buf.append((list(u'\u2800' * (curses.COLS - 1))))

    # draw_line(screen_buf)

    star = Body()
    star.pos = Vec(30, 10)
    star.mass = 1000.0

    satellite = Body()
    satellite.pos = Vec(10, 10)
    satellite.vel = Vec(0, 6)
    satellite.mass = 10.0

    r = 0

    t = 0
    freq = 100
    dt = 1.0/freq

    while True:
        d = distance(star, satellite)

        if d <= 1:
            break

        screen_buf = clear_buf()
        draw_pt(screen_buf, star.pos)
        draw_pt(screen_buf, satellite.pos)

        # Fg_mag = (G * star.mass * satellite.mass) / (d**2)
        # Fg = mul_s(sub(star.pos, satellite.pos), Fg_mag)

        # satellite.acc = div(Fg, satellite.mass)
        # satellite.vel = add(satellite.vel, mul_s(satellite.acc, dt))
        # satellite.pos = add(satellite.pos, mul_s(satellite.vel, dt))

        # draw_pt(screen_buf, star.pos)
        # draw_pt(screen_buf, satellite.pos)

        time.sleep(5)

        display(scr, screen_buf)
        t += dt

    # time.sleep(2)
    curses.endwin()             # Przywraca terminal do oryginalnych ustawień


def norm(pt1, pt2):
    dx = pt2.x - pt1.x
    dy = pt2.y - pt1.y

    return Vec(-dy, dx)

def mul_s(vec, val):
    return Vec(vec.x * val, vec.y * val)

def div(vec, val):
    return Vec(vec.x / val, vec.y / val)

def sub(pt1, pt2):
    return Vec(pt1.x - pt2.x, pt1.y - pt2.y)

def add(pt1, pt2):
    return Vec(pt1.x + pt2.x, pt1.y + pt2.y)


def setup():
    scr = curses.initscr()
    curses.start_color()        # Potrzebne do definiowania kolorów
    curses.use_default_colors() # Używaj kolorów terminala
    curses.halfdelay(5)         # Ile częśći sekundy czekamy na klawisz, od 1 do 255
    curses.noecho()             # Nie drukuje znaków na wejściu
    curses.curs_set(False)      # Wyłącza pokazywanie kursora
    scr.clear()

    return scr

def clear_buf():
    screen_buf = []
    for _ in range(curses.LINES):
        screen_buf.append((list(u'\u2800' * (curses.COLS - 1))))

    return screen_buf


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


def draw_pt(screen_buf, pt):
    if curses.LINES - 1 - int(pt.y / 4) < 0 or \
       curses.LINES - 1 - int(pt.y / 4) >= curses.LINES:
        return

    if int(pt.x / 2) < 0 or \
       int(pt.x / 2) >= curses.COLS:
        return

    x = int(pt.x)
    y = int(pt.y)
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


def distance(body1, body2):
    return math.sqrt((body1.pos.x - body2.pos.x)**2 + (body1.pos.y - body2.pos.y)**2)


def display(scr, screen_buf):
    scr.clear()

    for num, line in enumerate(screen_buf):
        scr.addstr(num, 0, u''.join(line).encode('utf-8'))
        # scr.addstr(num, 0, 'asdf')n)

    scr.refresh()


if __name__ == '__main__':
    main()

