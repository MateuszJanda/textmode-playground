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
GRID_SIZE = 46+2         # Grid size with boundaries around fluid
ITERATIONS = 4

# Screen parameters
NUM_OF_COLORS = 254
SPARE_FOR_DEFAULT_COLORS = 2
X_SHIFT = 0
Y_SHIFT = 0
LOWER_HALF_BLOCK = u'\u2584'

# Debug parameters
DEBUG = open('/dev/pts/1', 'w')
sys.stderr = DEBUG


def main():
    screen = Screen(colormap=cm.viridis)

    fluid = Fluid(diffusion=0, viscosity=0)

    fluid.add_density(x=GRID_SIZE//2, y=GRID_SIZE//2, amount=200)
    fluid.add_velocity(x=GRID_SIZE//2, y=GRID_SIZE//2, vel_x=100, vel_y=100)

    # Printaquarium borders
    render_aquarium_borders(screen)

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
        assert colormap.N == NUM_OF_COLORS + SPARE_FOR_DEFAULT_COLORS, "We cant initialize more than 256*256 pairs"

        for color_num in range(NUM_OF_COLORS):
            r, g, b = colormap.colors[color_num]
            ret = self._ncurses.init_extended_color(color_num, int(r*1000), int(g*1000), int(b*1000))
            if ret != 0:
                plog('init_extended_color error: %d, for color_num: %d' % (ret, color_num))
                raise RuntimeError

        for bg, fg in it.product(range(NUM_OF_COLORS), range(NUM_OF_COLORS)):
            # Start from 1 (0 is reserved by ncurses)
            pair_num = self.colors_to_pair_num(fg, bg)

            # Pair number 0 is reserved by lib, and can't be initialized
            if pair_num == 0:
                continue

            ret = self._ncurses.init_extended_pair(pair_num, fg, bg)
            if ret != 0:
                plog('init_extended_pair error: %d, for pair_num: %d' % (ret, pair_num))
                raise RuntimeError

    def _init_text_colors(self):
        """Reserver two color for text."""
        assert SPARE_FOR_DEFAULT_COLORS >= 2, 'There is no free color indexes for text colors.'
        # Reserve next two available indexes
        fg_color_num = NUM_OF_COLORS
        bg_color_num = NUM_OF_COLORS + 1

        r, g, b = 0, 0, 0
        ret = self._ncurses.init_extended_color(bg_color_num, int(r*1000), int(g*1000), int(b*1000))
        if ret != 0:
            plog('init_extended_color error: %d, for color_num: %d' % (ret, bg_color_num))
            raise RuntimeError

        r, g, b = 0.6, 0.6, 0.6
        ret = self._ncurses.init_extended_color(fg_color_num, int(r*1000), int(g*1000), int(b*1000))
        if ret != 0:
            plog('init_extended_color error: %d, for color_num: %d' % (ret, fg_color_num))
            raise RuntimeError

        # Set color under pair number 0
        ret = self._ncurses.assume_default_colors(fg_color_num, bg_color_num)
        if ret != 0:
            plog('assume_default_colors error: %d' % ret)
            raise RuntimeError

    def addstr(self, y, x, text, pair_num=0):
        """
        addstr - similar to curses.addstr function, however pair_num shouldn't
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

    def colors_to_pair_num(self, foreground, background):
        """Determine pair number for two colors."""
        pair_num = int(background) * NUM_OF_COLORS + int(foreground) + 1
        if pair_num == 0:
            pair_num = 1
        return pair_num

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
        self.density[y, x] += amount

    def add_velocity(self, x, y, vel_x, vel_y):
        self.vx[y, x] += vel_x
        self.vy[y, x] += vel_y


def render_fluid(screen, fluid):
    """Render fluid."""
    # Normalize density array
    norm_dens = fluid.density * 80
    # Set max possible color
    norm_dens[norm_dens>=NUM_OF_COLORS] = NUM_OF_COLORS - 1
    norm_dens = norm_dens.astype(int)

    y_shift = Y_SHIFT + 1
    x_shift = X_SHIFT + 1

    # Print debug info
    bg, fg = norm_dens[0:2, 0]
    pair_num = screen.colors_to_pair_num(fg, bg)
    screen.addstr(0 + y_shift, 48 + x_shift, LOWER_HALF_BLOCK, pair_num)
    screen.addstr(0 + y_shift, 51 + x_shift, 'bg: %d fg: %d pair_num: %d  ' % (bg, fg, pair_num))

    screen.addstr(1 + y_shift, 48 + x_shift, 'Max     : %6.4f      ' % np.max(fluid.density))
    screen.addstr(2 + y_shift, 48 + x_shift, 'Max norm: %d  ' % np.max(norm_dens))
    screen.addstr(3 + y_shift, 48 + x_shift, 'Min     : %6.4f      ' %  np.min(fluid.density))
    screen.addstr(4 + y_shift, 48 + x_shift, 'Min norm: %d  ' % np.min(norm_dens))

    # Print fluid
    for i in range(1, GRID_SIZE-1):
        for j in range(1, GRID_SIZE-1, 2):
            bg, fg = norm_dens[j:j+2, i]
            pair_num = screen.colors_to_pair_num(fg, bg)
            screen.addstr(j//2 + y_shift, (i - 1) + x_shift, LOWER_HALF_BLOCK, pair_num)


def render_aquarium_borders(screen):
    """Render aquarium borders."""
    vertical_border = '+' + '-' * (GRID_SIZE-2) + '+'
    screen.addstr(0 + Y_SHIFT, 0 + X_SHIFT, vertical_border)
    screen.addstr((GRID_SIZE-2)//2 + 1 + Y_SHIFT, 0 + X_SHIFT, vertical_border)

    for y in range((GRID_SIZE-2)//2):
        screen.addstr(y + 1 + Y_SHIFT, 0 + X_SHIFT, '|')
        screen.addstr(y + 1 + Y_SHIFT, (GRID_SIZE - 2) + 1 + X_SHIFT, '|')


def diffuse(b, x, x0, diff, dt):
    """
    Diffusion is the net movement of anything (for example dye) from
    a region of higher concentration to a region of lower concentration.
    """
    a = dt * diff * (GRID_SIZE - 2) * (GRID_SIZE - 2)
    linear_solver(b, x, x0, a, 1 + 4 * a)


def linear_solver(b, x, x0, a, c):
    """
    Solving a system of linear differential equation.
    """
    cRecip = 1 / c
    for k in range(ITERATIONS):
        for j in range(1, GRID_SIZE - 1):
            for i in range(1, GRID_SIZE - 1):
                x[j, i] = (x0[j, i] + a*(x[j, i+1] + x[j, i-1] + x[j+1, i] + x[j-1, i])) * cRecip

    set_boundry(b, x)


def project(velocX, velocY, p, div):
    """
    Keep all cells in equilibrium. For incompressible fluids amount of fluid
    in each cell has to stay constant. Amount of fluid going in has must be
    equal to the amount of fluid going out of cell.
    """
    cell_size = 1/GRID_SIZE
    for j in range(1, GRID_SIZE - 1):
        for i in range(1, GRID_SIZE - 1):
            div[j, i] = -0.5 * (velocX[j, i+1] - velocX[j, i-1] + velocY[j+1, i] - velocY[j-1, i]) * cell_size
            p[j, i] = 0

    set_boundry(0, div)
    set_boundry(0, p)
    linear_solver(0, p, div, 1, 4)

    for j in range(1, GRID_SIZE - 1):
        for i in range(1, GRID_SIZE - 1):
            velocX[j, i] -= 0.5 * (p[j, i+1] - p[j, i-1]) / cell_size
            velocY[j, i] -= 0.5 * (p[j+1, i] - p[j-1, i]) / cell_size

    set_boundry(1, velocX)
    set_boundry(2, velocY)


def advect(b, d, d0, velocX, velocY, dt):
    """
    Advection is the transport of a substance or quantity by fluid in this way
    that velocity of transported substance is equal to velocity of fluid.
    """
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


def set_boundry(b, matrix):
    """
    Keep fluid from leaking out of the box. Every velocity in the layer next to
    this outer layer is mirrored.
    """
    for i in range(1, GRID_SIZE-1):
        if b == 2:
            matrix[0, i] = -matrix[1, i]
        else:
            matrix[0, i] = matrix[1, i]

        if b == 2:
            matrix[GRID_SIZE-1, i] = -matrix[GRID_SIZE-2, i]
        else:
            matrix[GRID_SIZE-1, i] = matrix[GRID_SIZE-2, i]

    for j in range(1, GRID_SIZE-1):
        if b == 1:
            matrix[j, 0] = -matrix[j, 1]
        else:
            matrix[j, 0] = matrix[j, 1]

        if b == 1:
            matrix[j, 0] = -matrix[j, 1]
        else:
            matrix[j, 0] = matrix[j, 1]

    matrix[0, 0]                       = 0.5 * (matrix[0, 1] + matrix[1, 0])
    matrix[GRID_SIZE-1, 0]            = 0.5 * (matrix[GRID_SIZE-1, 1] + matrix[GRID_SIZE-2, 0])
    matrix[0, GRID_SIZE-1]            = 0.5 * (matrix[0, GRID_SIZE-2] + matrix[1, GRID_SIZE-1])
    matrix[GRID_SIZE-1, GRID_SIZE-1] = 0.5 * (matrix[GRID_SIZE-1, GRID_SIZE-2] + matrix[GRID_SIZE-2, GRID_SIZE-1])


if __name__ == '__main__':
    main()
