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
        self.dt = dt                   # time step
        self.diff = diffusion          # diffusion - dyfuzja
        self.visc = viscosity          # viscosity - lepkość

        self.s = new float[N*N]        # prev density
        self.density = new float[N*N]

        self.Vx = new float[N*N]
        self.Vy = new float[N*N]

        self.Vx0 = new float[N*N]      # prev velocity X
        self.Vy0 = new float[N*N]      # prev velocity Y


def main():
    pass


if __name__ == '__main__':
    main()
