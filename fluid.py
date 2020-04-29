#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

import numpy as np


N = 256


class Fluid:
    def __init__(self, dt, diffusion, viscosity):
        self.size = N
        self.dt = dt                            # time step
        self.diff = diffusion                   # diffusion - dyfuzja
        self.visc = viscosity                   # viscosity - lepkość

        self.s = np.zeros(shape=(N, N))         # prev density
        self.density = np.zeros(shape=(N, N))

        self.Vx = np.zeros(shape=(N, N))
        self.Vy = np.zeros(shape=(N, N))

        self.Vx0 = np.zeros(shape=(N, N))       # prev velocity X
        self.Vy0 = np.zeros(shape=(N, N))       # prev velocity Y


def main():
    fluid = Fluid(dt=0.1, diffusion=0, viscosity=0)


if __name__ == '__main__':
    main()
