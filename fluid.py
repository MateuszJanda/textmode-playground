#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

"""
Credits:
- "Real-Time Fluid Dynamics for Game" by Jos Stam - https://pdfs.semanticscholar.org/847f/819a4ea14bd789aca8bc88e85e906cfc657c.pdf
- "Fluid Simulation for Dummies" by Mike Ash - https://mikeash.com/pyblog/fluid-simulation-for-dummies.html
- "Coding Challenge #132: Fluid Simulation" - https://www.youtube.com/watch?v=alhpH6ECFvQ
- "Coding Challenge #132: Fluid Simulation"- https://github.com/CodingTrain/website/tree/master/CodingChallenges/CC_132_FluidSimulation/Processing/CC_132_FluidSimulation
"""

import time
import itertools as it
import ctypes as ct
import matplotlib.cm as cm
import numpy as np


N = 48
ITERATIONS = 4

NUM_OF_COLORS = 256
Y_SHIFT = 0
X_SHIFT = 0


DEBUG = open('/dev/pts/1', 'w')


def main():
    screen = Screen(colormap=cm.viridis)

    fluid = Fluid(dt=0.1, diffusion=0, viscosity=0)

    fluid.add_density(N/2, N/2, 200)
    fluid.add_velocity(N/2, N/2, 100, 100)

    t = 0
    while True:
        # screen.erase()

        diffuse(1, fluid.vx0, fluid.vx, fluid.visc, fluid.dt)
        diffuse(2, fluid.vy0, fluid.vy, fluid.visc, fluid.dt)

        project(fluid.vx0, fluid.vy0, fluid.vx, fluid.vy)

        advect(1, fluid.vx, fluid.vx0, fluid.vx0, fluid.vy0, fluid.dt)
        advect(2, fluid.vy, fluid.vy0, fluid.vx0, fluid.vy0, fluid.dt)

        project(fluid.vx, fluid.vy, fluid.vx0, fluid.vy0)

        diffuse(0, fluid.s, fluid.density, fluid.diff, fluid.dt)
        advect(0, fluid.density, fluid.s, fluid.vx, fluid.vy, fluid.dt)

        render_fluid(screen, fluid)

        time.sleep(0.5)
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


        screen.refresh()
        # return

    screen.endwin()


def show(*args, **kwargs):
    print(*args, file=DEBUG)
    pass


class Screen:
    A_NORMAL = 0

    def __init__(self, colormap):
        self._ncurses = ct.CDLL('./libncursesw.so.6.1')
        self._setup_ncurses()
        self._init_colors(colormap)

    def _setup_ncurses(self):
        """Setup ncurses screen."""
        self._win = self._ncurses.initscr()
        self._ncurses.start_color()
        self._ncurses.halfdelay(5)
        self._ncurses.noecho()
        self._ncurses.curs_set(0)
        self.LINES, self.COLS = self._getmaxyx()

    def _getmaxyx(self):
       y = self._ncurses.getmaxy(self._win)
       x = self._ncurses.getmaxx(self._win)
       return y, x-1

    def _init_colors(self, colormap):
        """Initi color pairs based on matplotlib colormap."""
        for color_num in range(colormap.N):
            r, g, b = colormap.colors[color_num]
            ret = self._ncurses.init_extended_color(color_num, int(r*1000), int(g*1000), int(b*1000))
            if ret != 0:
                show('init_extended_color error: %d, for color_num: %d' % (ret, color_num))
                raise RuntimeError

        assert colormap.N == 256

        for bg, fg in it.product(range(colormap.N), range(colormap.N)):
            pair_num = bg * colormap.N + fg

            if pair_num == 0:
                continue

            ret = self._ncurses.init_extended_pair(pair_num, fg, bg)
            if ret != 0:
                show('init_extended_pair error: %d, for pair_num: %d' % (ret, pair_num))
                raise RuntimeError

    def addstr(self, y, x, text, pair_num):
        """
        addstr - similar to curses.addstr function, however pari_num shouldn't
        be converted by curses.color_pair or similar.
        """
        pair_num_short = ct.cast((ct.c_int*1)(pair_num), ct.POINTER(ct.c_short)).contents
        pair_num_pt = ct.c_int(pair_num)
        ret = self._ncurses.attr_set(ct.c_int(self.A_NORMAL), pair_num_short, ct.pointer(pair_num_pt))
        if ret != 0:
            show('attr_set error %d, pair_num: %d' % (ret, pair_num))
            raise RuntimeError

        ret = self._ncurses.mvprintw(y, x, text.encode('utf-8'))
        if ret != 0:
            show('mvprintw error: %d, y: %d, x: %d, pair_num: %d' % (ret, y, x, pair_num))
            raise RuntimeError

    def refresh(self):
        """Refresh screen."""
        self._ncurses.refresh()

    def endwin(self):
        """End when after pressing q."""
        ch = self._ncurses.getch()
        while ch != ord('q'):
            ch = self._ncurses.getch()
        self._ncurses.endwin()

        show('The end.')


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


def colors_to_pair_num(foreground, background):
    pair_num = (background*NUM_OF_COLORS + foreground) % NUM_OF_COLORS**2
    if pair_num == 0:
        pair_num = 1
    return int(pair_num)


def render_fluid(screen, fluid):
    LOWER_HALF_BLOCK = u'\u2584'

    # ddd = np.log10(fluid.density *100 + 100)
    # ddd = fluid.density *100
    # ddd = np.log10(fluid.density) *100
    max_val = int(np.max(fluid.density) * 20) % NUM_OF_COLORS
    screen.addstr(0 + Y_SHIFT, 51 + X_SHIFT, '█', max_val)
    screen.addstr(3 + Y_SHIFT, 51 + X_SHIFT, str(max_val) + '   ', 255)
    screen.addstr(4 + Y_SHIFT, 51 + X_SHIFT, str(np.max(fluid.density)) + '   ', 255)

    for i in range(N):
        for j in range(0, N, 2):
            bg = int((fluid.density[j, i] * 20) % NUM_OF_COLORS)
            fg = int((fluid.density[j+1, i] * 20) % NUM_OF_COLORS)
            # if np.isinf(ddd[j, i]):
            #     bg = 0
            # else:
            #     bg = int(ddd[j, i]) % NUM_OF_COLORS
            # if np.isinf(ddd[j+1, i]):
            #     fg = 0
            # fg = int(ddd[j+1, i]) % NUM_OF_COLORS

            # print('render bg-fg', bg, fg, file=DEBUG)

            pair_num = colors_to_pair_num(fg, bg)
            screen.addstr(int(j/2) + Y_SHIFT, i + X_SHIFT, LOWER_HALF_BLOCK, pair_num)
            # print('render pair_num', pair_num, file=DEBUG)
            # screen.addstr(int(j/2) + Y_SHIFT, i + X_SHIFT, 'a', curses.color_pair(5050))

            if i == 46 and j == 46:
                text = 'pair_num: ' + str(pair_num) + ' : ' + str(bg) + ' ' + str(fg) + ' ' + str(bg - fg)
                # screen.addstr(0 + Y_SHIFT, 51 + X_SHIFT, LOWER_HALF_BLOCK, pair_num)
                screen.addstr(1 + Y_SHIFT, 51 + X_SHIFT, text, 255)
                text = str(fluid.density[j, i]) + ' ' + str(fluid.density[j+1, i]) + ' ' + str(fluid.density[j, i] - fluid.density[j+1, i])
                screen.addstr(2 + Y_SHIFT, 51 + X_SHIFT, text, 255)

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
    main()
