#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

import curses
import time
import numpy as np


N = 256
ITERATION = 4


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
        self.density[y, x] += amount

    def add_velocity(self, x, y, amount_x, amount_y):
        self.vx[y, x] += amount_x
        self.vy[y, x] += amount_y


def main():
    setup_curses(scr)

    fluid = Fluid(dt=0.1, diffusion=0, viscosity=0)

    while True:
        scr.clear()

        diffuse(1, fluid.vx0, fluid.vx, fluid.visc, fluid.dt)
        diffuse(2, fluid.Vy0, fluid.Vy, fluid.visc, fluid.dt)

        project(fluid.Vx0, fluid.Vy0, fluid.Vx, fluid.Vy)

        advect(1, fluid.Vx, fluid.Vx0, fluid.Vx0, fluid.Vy0, fluid.dt)
        advect(2, fluid.Vy, fluid.Vy0, fluid.Vx0, fluid.Vy0, fluid.dt)

        project(fluid.Vx, fluid.Vy, fluid.Vx0, fluid.Vy0)

        diffuse(0, fluid.s, fluid.density, fluid.diff, fluid.dt)
        advect(0, fluid.density, fluid.s, fluid.Vx, fluid.Vy, fluid.dt)

        draw_fluid(scr, color)

        time.sleep(0.01)
        scr.refresh()



def setup_curses(scr):
    curses.start_color()
    curses.halfdelay(1)
    curses.curs_set(False)

    curses.init_color(0, *BLACK_RGB)
    curses.init_color(1, *WHITE_RGB)
    curses.init_color(2, *BLUE_RGB)
    curses.init_color(3, *RED_RGB)

    curses.init_pair(WHITE_ID, 1, 0)
    curses.init_pair(BLUE_ID, 2, 0)
    curses.init_pair(RED_ID, 3, 0)
    curses.init_pair(BACKGROUND_ID, 0, 0)

    scr.bkgd(' ', curses.color_pair(BACKGROUND_ID))
    scr.clear()


def draw_fluid(scr, color):
    for y, text in enumerate(SHIFT.split('\n')):
        scr.addstr(y + Y_SHIFT, X_SHIFT, text, curses.color_pair(color))



def diffuse(b,  x, x0, diff, dt):
    a = dt * diff * (N - 2) * (N - 2)
    linear_solver(b, x, x0, a, 1 + 4 * a)


def linear_solver(b, x, x0, a, c):
    cRecip = 1 / c
    for k in range(ITERATION):
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
            velocX[j, i] -= 0.f * (p[j, i+1] - p[j, i-1]) * N
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
            if x > N + 0.5:
                x = N + 0.5
            i0 = floor(x)
            i1 = i0 + 1.0
            if y < 0.5:
                y = 0.5
            if y > N + 0.5:
                y = N + 0.5
            j0 = floor(y)
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
    main()
