#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

"""
Credits:
- "Real-Time Fluid Dynamics for Game" by Jos Stam
  https://pdfs.semanticscholar.org/847f/819a4ea14bd789aca8bc88e85e906cfc657c.pdf
- "Fluid Simulation for Dummies" by Mike Ash
  https://mikeash.com/pyblog/fluid-simulation-for-dummies.html
- "Coding Challenge #132: Fluid Simulation"
  https://www.youtube.com/watch?v=alhpH6ECFvQ
- "Coding Challenge #132: Fluid Simulation"
  https://github.com/CodingTrain/website/tree/master/CodingChallenges/CC_132_FluidSimulation/Processing/CC_132_FluidSimulation
"""

import os
import sys
import time
import itertools as it
import ctypes as ct
import matplotlib.cm as cm
import numpy as np


# Engine parameters
GRID_SIZE = 48
ITERATIONS = 4

# Screen parameters
NUM_OF_COLORS = 256
X_SHIFT = 0
Y_SHIFT = 0
LOWER_HALF_BLOCK = u'\u2584'

# Debug parameters
DEBUG = open('/dev/pts/1', 'w')
sys.stderr = DEBUG


def main():
    screen = Screen(colormap=cm.viridis)

    fluid = Fluid(diffusion=0, viscosity=0)

    fluid.add_density(x=GRID_SIZE/2, y=GRID_SIZE/2, amount=200)
    fluid.add_velocity(x=GRID_SIZE/2, y=GRID_SIZE/2, vel_x=100, vel_y=100)

    dt = 0.1

    while True:
        tic = time.time()

        diffuse(1, fluid.vx0, fluid.vx, fluid.visc, dt)
        diffuse(2, fluid.vy0, fluid.vy, fluid.visc, dt)

        project(fluid.vx0, fluid.vy0, fluid.vx, fluid.vy)

        advect(1, fluid.vx, fluid.vx0, fluid.vx0, fluid.vy0, dt)
        advect(2, fluid.vy, fluid.vy0, fluid.vx0, fluid.vy0, dt)

        project(fluid.vx, fluid.vy, fluid.vx0, fluid.vy0)

        diffuse(0, fluid.s, fluid.density, fluid.diff, dt)
        advect(0, fluid.density, fluid.s, fluid.vx, fluid.vy, dt)

        render_fluid(screen, fluid)

        # Sleep only if extra time left
        delay = max(0, dt - (time.time() - tic))
        time.sleep(delay)

        screen.refresh()

    screen.endwin()


def plog(*args, **kwargs):
    """print replacement for logging on other console."""
    if 'DEBUG' in globals():
        print(*args, file=DEBUG)


class Screen:
    # As in Python curses
    A_NORMAL = 0

    def __init__(self, colormap):
        if not os.path.isfile('./libncursesw.so.6.1'):
            print("Can't find ./libncursesw.so.6.1")
            raise RuntimeError
        self._ncurses = ct.CDLL('./libncursesw.so.6.1')
        self._setup_ncurses()
        self._init_colors(colormap)
        self._init_text_colors()

    def _setup_ncurses(self):
        """Setup ncurses screen."""
        self._win = self._ncurses.initscr()
        self._ncurses.start_color()
        self._ncurses.halfdelay(5)
        self._ncurses.noecho()
        self._ncurses.curs_set(0)
        self.LINES, self.COLS = self._getmaxyx()

    def _getmaxyx(self):
        """Determine max screen size."""
        y = self._ncurses.getmaxy(self._win)
        x = self._ncurses.getmaxx(self._win)
        return y, x-1

    def _init_colors(self, colormap):
        """Initialize color pairs based on matplotlib colormap."""
        assert colormap.N == 256, "We cant initialize more than 256*256 pairs"

        for color_num in range(colormap.N-2):
            r, g, b = colormap.colors[color_num]
            ret = self._ncurses.init_extended_color(color_num, int(r*1000), int(g*1000), int(b*1000))
            if ret != 0:
                plog('init_extended_color error: %d, for color_num: %d' % (ret, color_num))
                raise RuntimeError

        for bg, fg in it.product(range(colormap.N-2), range(colormap.N-2)):
            pair_num = bg * colormap.N + fg

            # Pair number 0 is reserved by lib, and can't be initialized
            if pair_num == 0:
                continue

            ret = self._ncurses.init_extended_pair(pair_num, fg, bg)
            if ret != 0:
                plog('init_extended_pair error: %d, for pair_num: %d' % (ret, pair_num))
                raise RuntimeError

    def _init_text_colors(self):
        """Reserver two color for text."""
        bg_color_num = 255
        fg_color_num = 254

        r, g, b = 0, 0, 0
        ret = self._ncurses.init_extended_color(bg_color_num, int(r*1000), int(g*1000), int(b*1000))
        if ret != 0:
            plog('init_extended_color error: %d, for color_num: %d' % (ret, bg_color_num))
            raise RuntimeError

        r, g, b = 0.5, 0.5, 0.5
        ret = self._ncurses.init_extended_color(fg_color_num, int(r*1000), int(g*1000), int(b*1000))
        if ret != 0:
            plog('init_extended_color error: %d, for color_num: %d' % (ret, fg_color_num))
            raise RuntimeError

        # Set color under pair number 0
        ret = self._ncurses.assume_default_colors(fg_color_num, bg_color_num)
        if ret != 0:
            plog('assume_default_colors error: %d' % ret)
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
            plog('attr_set error %d, pair_num: %d' % (ret, pair_num))
            raise RuntimeError

        ret = self._ncurses.mvprintw(y, x, text.encode('utf-8'))
        if ret != 0:
            plog('mvprintw error: %d, y: %d, x: %d, pair_num: %d' % (ret, y, x, pair_num))
            raise RuntimeError

    def refresh(self):
        """Refresh screen."""
        self._ncurses.refresh()

    def endwin(self):
        """End ncurses."""
        self._ncurses.endwin()
        plog('The end.')


class Fluid:
    def __init__(self, diffusion, viscosity):
        self.diff = diffusion                   # diffusion - dyfuzja
        self.visc = viscosity                   # viscosity - lepkość

        self.s = np.zeros(shape=(GRID_SIZE, GRID_SIZE))     # prev density
        self.density = np.zeros(shape=(GRID_SIZE, GRID_SIZE))

        self.vx = np.zeros(shape=(GRID_SIZE, GRID_SIZE))
        self.vy = np.zeros(shape=(GRID_SIZE, GRID_SIZE))

        self.vx0 = np.zeros(shape=(GRID_SIZE, GRID_SIZE))   # prev velocity X
        self.vy0 = np.zeros(shape=(GRID_SIZE, GRID_SIZE))   # prev velocity Y

    def add_density(self, x, y, amount):
        self.density[int(y), int(x)] += amount

    def add_velocity(self, x, y, vel_x, vel_y):
        y = int(y)
        x = int(x)
        self.vx[y, x] += vel_x
        self.vy[y, x] += vel_y


def colors_to_pair_num(foreground, background):
    """Determine pair number for two colors."""
    pair_num = (background*NUM_OF_COLORS + foreground) % NUM_OF_COLORS**2
    if pair_num == 0:
        pair_num = 1
    return int(pair_num)


def render_fluid(screen, fluid):
    """Render fluid."""
    # ddd = np.log10(fluid.density *100 + 100)
    # ddd = fluid.density *100
    # ddd = np.log10(fluid.density) *100
    # norml_dens = (np.max(fluid.density) * 20) % NUM_OF_COLORS
    norml_dens = np.copy(fluid.density)
    norml_dens = fluid.density + 1
    norml_dens = (fluid.density * 20)
    norml_dens[norml_dens>253] = 253
    norml_dens = norml_dens.astype(int)

    max_val = int(np.max(fluid.density) * 20) % NUM_OF_COLORS
    screen.addstr(0 + Y_SHIFT, 51 + X_SHIFT, '█', max_val)
    screen.addstr(3 + Y_SHIFT, 51 + X_SHIFT, str(max_val) + '   ', 0)
    screen.addstr(4 + Y_SHIFT, 51 + X_SHIFT, str(np.max(fluid.density)) + '   ', 0)

    for i in range(GRID_SIZE):
        for j in range(0, GRID_SIZE, 2):
            bg, fg = norml_dens[j:j+2, i]

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
                screen.addstr(1 + Y_SHIFT, 51 + X_SHIFT, text, 0)
                text = str(fluid.density[j, i]) + ' ' + str(fluid.density[j+1, i]) + ' ' + str(fluid.density[j, i] - fluid.density[j+1, i])
                screen.addstr(2 + Y_SHIFT, 51 + X_SHIFT, text, 0)

            # return


def diffuse(b, x, x0, diff, dt):
    a = dt * diff * (GRID_SIZE - 2) * (GRID_SIZE - 2)
    linear_solver(b, x, x0, a, 1 + 4 * a)


def linear_solver(b, x, x0, a, c):
    cRecip = 1 / c
    for k in range(ITERATIONS):
        for j in range(1, GRID_SIZE - 1):
            for i in range(1, GRID_SIZE - 1):
                x[j, i] = (x0[j, i] + a*(x[j, i+1] + x[j, i-1] + x[j+1, i] + x[j-1, i])) * cRecip

    set_boundry(b, x)


def project(velocX, velocY, p, div):
    for j in range(1, GRID_SIZE - 1):
        for i in range(1, GRID_SIZE - 1):
            div[j, i] = -0.5 * (velocX[j, i+1] - velocX[j, i-1] + velocY[j+1, i] - velocY[j-1, i]) / GRID_SIZE
            p[j, i] = 0

    set_boundry(0, div)
    set_boundry(0, p)
    linear_solver(0, p, div, 1, 4)

    for j in range(1, GRID_SIZE - 1):
        for i in range(1, GRID_SIZE - 1):
            velocX[j, i] -= 0.5 * (p[j, i+1] - p[j, i-1]) * GRID_SIZE
            velocY[j, i] -= 0.5 * (p[j+1, i] - p[j-1, i]) * GRID_SIZE

    set_boundry(1, velocX)
    set_boundry(2, velocY)


def advect(b, d, d0, velocX, velocY, dt):
    dtx = dt * (GRID_SIZE - 2)
    dty = dt * (GRID_SIZE - 2)

    for j in range(1, GRID_SIZE-1):
        for i in range(1, GRID_SIZE-1):
            tmp1 = dtx * velocX[j, i]
            tmp2 = dty * velocY[j, i]
            x = i - tmp1
            y = j - tmp2

            if x < 0.5:
                x = 0.5
            if x > (GRID_SIZE-1-1) + 0.5:
                x = (GRID_SIZE-1-1) + 0.5
            i0 = np.floor(x)
            i1 = i0 + 1.0
            if y < 0.5:
                y = 0.5
            if y > (GRID_SIZE-1-1) + 0.5:
                y = (GRID_SIZE-1-1) + 0.5
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
    for i in range(GRID_SIZE-1):
        if b == 2:
            x[0, i] = -x[1, i]
        else:
            x[0, i] = x[1, i]

        if b == 2:
            x[GRID_SIZE-1, i] = -x[GRID_SIZE-2, i]
        else:
            x[GRID_SIZE-1, i] = x[GRID_SIZE-2, i]

    for j in range(1, GRID_SIZE-1):
        if b == 1:
            x[j, 0] = -x[j, 1]
        else:
            x[j, 0] = x[j, 1]

        if b == 1:
            x[j, 0] = -x[j, 1]
        else:
            x[j, 0] = x[j, 1]

    x[0, 0] = 0.5 * (x[0, 1] + x[1, 0])
    x[GRID_SIZE-1, 0] = 0.5 * (x[GRID_SIZE-1, 1] + x[GRID_SIZE-2, 0])
    x[0, GRID_SIZE-1] = 0.5 * (x[0, GRID_SIZE-2] + x[1, GRID_SIZE-1])
    x[GRID_SIZE-1, GRID_SIZE-1] = 0.5 * (x[GRID_SIZE-1, GRID_SIZE-2] + x[GRID_SIZE-2, GRID_SIZE-1])


if __name__ == '__main__':
    main()
