#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

import time
import curses
import locale
import numpy as np


N = 48
ITERATION = 4

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

    fluid.add_density(N/2, N/2, 100)
    fluid.add_velocity(N/2, N/2, 100, 100)

    while True:
        scr.clear()

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
        scr.refresh()


def setup_curses(scr):
    curses.start_color()
    curses.halfdelay(1)
    curses.curs_set(False)

    for color_id in range(128):
        curses.init_color(color_id, *gray_rgb(color_id*2))

    for bg_id in range(128):
        for fg_id in range(128):
            curses.init_pair(bg_id*128 + fg_id + 1, fg_id, bg_id)

    scr.bkgd(' ', curses.color_pair(0))
    scr.clear()


def gray_rgb(val):
    return (val*1000)//255, (val*1000)//255, (val*1000)//255


Y_SHIFT = 0
X_SHIFT = 0


def render_fluid(scr, fluid):
    LOWER_HALF_BLOCK = u'\u2584'

    for i in range(N):
        for j in range(0, N, 2):
            bg = (fluid.density[j, i] + 50) % 128
            fg = (fluid.density[j+1, i] + 50) % 128

            color = int(bg * 128 + fg)
            scr.addstr(int(j/2) + Y_SHIFT, i + X_SHIFT, LOWER_HALF_BLOCK, curses.color_pair(color))


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
