#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

import numpy as np


N = 256
ITERATION = 10


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
    fluid = Fluid(dt=0.1, diffusion=0, viscosity=0)


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



if __name__ == '__main__':
    main()
