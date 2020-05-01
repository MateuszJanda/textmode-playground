#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

"""
Credits:
- "Coding Challenge #132: Fluid Simulation" - https://www.youtube.com/watch?v=alhpH6ECFvQ
- "Fluid Simulation for Dummies" by Mike Ash - https://mikeash.com/pyblog/fluid-simulation-for-dummies.html
- "Real-Time Fluid Dynamics for Game" by Jos Stam - https://pdfs.semanticscholar.org/847f/819a4ea14bd789aca8bc88e85e906cfc657c.pdf
"""

import time
import curses
import locale
import numpy as np


N = 48
ITERATIONS = 4

NUM_OF_COLORS = 16
Y_SHIFT = 0
X_SHIFT = 0


GLOBAL_PAIR_ID = 255


DEBUG = open('/dev/pts/1', 'w')


class Fluid:
    def __init__(self, dt, diffusion, viscosity):
        self.size = N
        self.dt = dt                            # time step
        self.diff = diffusion                   # diffusion - dyfuzja
        self.visc = viscosity                   # viscosity - lepkość

        self.s = np.zeros(shape=(N, N))         # prev density
        self.density = np.zeros(shape=(N, N))

        self.vx = np.zeros(shape=(N, N))
        self.vy = np.zeros(shape=(N, N))

        self.vx0 = np.zeros(shape=(N, N))       # prev velocity X
        self.vy0 = np.zeros(shape=(N, N))       # prev velocity Y

    def add_density(self, x, y, amount):
        self.density[int(y), int(x)] += amount

    def add_velocity(self, x, y, amount_x, amount_y):
        y = int(y)
        x = int(x)
        self.vx[y, x] += amount_x
        self.vy[y, x] += amount_y


def main(scr):
    setup_curses(scr)

    fluid = Fluid(dt=0.1, diffusion=0, viscosity=0)

    fluid.add_density(N/2, N/2, 1000)
    fluid.add_velocity(N/2, N/2, 100, 100)

    t = 0
    while True:
        scr.erase()

        diffuse(1, fluid.vx0, fluid.vx, fluid.visc, fluid.dt)
        diffuse(2, fluid.vy0, fluid.vy, fluid.visc, fluid.dt)

        project(fluid.vx0, fluid.vy0, fluid.vx, fluid.vy)

        advect(1, fluid.vx, fluid.vx0, fluid.vx0, fluid.vy0, fluid.dt)
        advect(2, fluid.vy, fluid.vy0, fluid.vx0, fluid.vy0, fluid.dt)

        project(fluid.vx, fluid.vy, fluid.vx0, fluid.vy0)

        diffuse(0, fluid.s, fluid.density, fluid.diff, fluid.dt)
        advect(0, fluid.density, fluid.s, fluid.vx, fluid.vy, fluid.dt)

        render_fluid(scr, fluid)

        time.sleep(0.01)
        t += 0.01
        # if t >= 1:
        if False:
            for line in fluid.density:
                text = ''
                for val in line:
                    text += ' ' + str(val)
                print(text, file=DEBUG)
            print('===', np.max(fluid.density), np.min(fluid.density), file=DEBUG)
            break


        scr.refresh()
        # return


def setup_curses(scr):
    """Setup curses environment and colors settings."""
    curses.start_color()
    curses.halfdelay(1)
    curses.curs_set(False)      # Disable blinking cursor

    # The value of color_number must be between 0 and COLORS
    assert NUM_OF_COLORS < curses.COLORS

    for color_number in range(NUM_OF_COLORS):
        color_value = color_number * 256//NUM_OF_COLORS

        curses.init_color(color_number, *gray_rgb(color_value))
    #     if color_number == 50:
    #         print('init_color', gray_rgb(color_value), file=DEBUG)

    # curses.init_color(50, 500, 500, 500)
    # curses.init_color(1, 1, 1, 1)

    # Setup colors
    assert NUM_OF_COLORS*NUM_OF_COLORS <= curses.COLOR_PAIRS
    # Actually because of some bug in Python curses support only 256 color pairs
    assert NUM_OF_COLORS*NUM_OF_COLORS <= 256

    for bg in range(NUM_OF_COLORS):
        for fg in range(NUM_OF_COLORS):
            pair_id = colors_to_pair_id(fg, bg)
            curses.init_pair(pair_id, fg, bg)

            # if pair_id == 5050:
            #     print('init_pair', fg, bg, file=DEBUG)

    # curses.init_pair(1, 50, 50)
    # curses.init_pair(GLOBAL_PAIR_ID, 50, 50)
    # curses.init_pair(1, 1, 1)

    scr.bkgd(' ', curses.color_pair(0))
    scr.clear()


def gray_rgb(val):
    return (val*1000)//256, (val*1000)//256, (val*1000)//256


def colors_to_pair_id(foreground, background):
    pair_id = (background*NUM_OF_COLORS + foreground) % NUM_OF_COLORS**2
    if pair_id == 0:
        pair_id = 1
    return int(pair_id)


def render_fluid(scr, fluid):
    LOWER_HALF_BLOCK = u'\u2584'

    for i in range(N):
        for j in range(0, N, 2):
            bg = int((fluid.density[j, i] + 50) % NUM_OF_COLORS)
            fg = int((fluid.density[j+1, i] + 50) % NUM_OF_COLORS)

            # print('render bg-fg', bg, fg, file=DEBUG)

            pair_id = colors_to_pair_id(fg, bg)
            scr.addstr(int(j/2) + Y_SHIFT, i + X_SHIFT, LOWER_HALF_BLOCK, curses.color_pair(pair_id))
            # print('render pair_id', pair_id, file=DEBUG)
            # scr.addstr(int(j/2) + Y_SHIFT, i + X_SHIFT, 'a', curses.color_pair(5050))

            if i == 46 and j == 46:
                text = 'pair_id: ' + str(pair_id) + ' : ' + str(bg) + ' ' + str(fg) + ' ' + str(bg - fg)
                scr.addstr(0 + Y_SHIFT, 51 + X_SHIFT, LOWER_HALF_BLOCK, curses.color_pair(pair_id))
                scr.addstr(1 + Y_SHIFT, 51 + X_SHIFT, text, curses.color_pair(0))
                text = str(fluid.density[j, i]) + ' ' + str(fluid.density[j+1, i]) + ' ' + str(fluid.density[j, i] - fluid.density[j+1, i])
                scr.addstr(2 + Y_SHIFT, 51 + X_SHIFT, text, curses.color_pair(0))

            # return


def diffuse(b,  x, x0, diff, dt):
    a = dt * diff * (N - 2) * (N - 2)
    linear_solver(b, x, x0, a, 1 + 4 * a)


def linear_solver(b, x, x0, a, c):
    cRecip = 1 / c
    for k in range(ITERATIONS):
        for j in range(1, N - 1):
            for i in range(1, N - 1):
                x[j, i] = (x0[j, i] + a*(x[j, i+1] + x[j, i-1] + x[j+1, i] + x[j-1, i])) * cRecip

    set_boundry(b, x)


def project(velocX, velocY, p, div):
    for j in range(1, N - 1):
        for i in range(1, N - 1):
            div[j, i] = -0.5 * (velocX[j, i+1] - velocX[j, i-1] + velocY[j+1, i] - velocY[j-1, i]) / N
            p[j, i] = 0

    set_boundry(0, div)
    set_boundry(0, p)
    linear_solver(0, p, div, 1, 4)

    for j in range(1, N - 1):
        for i in range(1, N - 1):
            velocX[j, i] -= 0.5 * (p[j, i+1] - p[j, i-1]) * N
            velocY[j, i] -= 0.5 * (p[j+1, i] - p[j-1, i]) * N

    set_boundry(1, velocX)
    set_boundry(2, velocY)


def advect(b, d, d0, velocX, velocY, dt):
    dtx = dt * (N - 2)
    dty = dt * (N - 2)

    for j in range(1, N-1):
        for i in range(1, N-1):
            tmp1 = dtx * velocX[j, i]
            tmp2 = dty * velocY[j, i]
            x    = i - tmp1
            y    = j - tmp2

            if x < 0.5:
                x = 0.5
            if x > (N-1-1) + 0.5:
                x = (N-1-1) + 0.5
            i0 = np.floor(x)
            i1 = i0 + 1.0
            if y < 0.5:
                y = 0.5
            if y > (N-1-1) + 0.5:
                y = (N-1-1) + 0.5
            j0 = np.floor(y)
            j1 = j0 + 1.0

            s1 = x - i0
            s0 = 1 - s1
            t1 = y - j0
            t0 = 1 - t1

            i0i = int(i0)
            i1i = int(i1)
            j0i = int(j0)
            j1i = int(j1)

            d[j, i] = s0 * (t0 * d0[j0i, i0i] + t1 * d0[j1i, i0i]) + \
                      s1 * (t0 * d0[j0i, i1i] + t1 * d0[j1i, i1i])

    set_boundry(b, d)


def set_boundry(b, x):
    for i in range(N-1):
        if b == 2:
            x[0, i] = -x[1, i]
        else:
            x[0, i] = x[1, i]

        if b == 2:
            x[N-1, i] = -x[N-2, i]
        else:
            x[N-1, i] = x[N-2, i]

    for j in range(1, N-1):
        if b == 1:
            x[j, 0] = -x[j, 1]
        else:
            x[j, 0] = x[j, 1]

        if b == 1:
            x[j, 0] = -x[j, 1]
        else:
            x[j, 0] = x[j, 1]

    x[0, 0] = 0.5 * (x[0, 1] + x[1, 0])
    x[N-1, 0] = 0.5 * (x[N-1, 1] + x[N-2, 0])
    x[0, N-1] = 0.5 * (x[0, N-2] + x[1, N-1])
    x[N-1, N-1] = 0.5 * (x[N-1, N-2] + x[N-2, N-1])


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
