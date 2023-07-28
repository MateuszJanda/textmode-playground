#!/usr/bin/env python3

# Author: Mateusz Janda <mateusz janda at gmail com>
# Site: github.com/MateuszJanda/textmode-playground
# Ad maiorem Dei gloriam

"""
Credits:
- "Real-Time Fluid Dynamics for Game" by Jos Stam
  https://pdfs.semanticscholar.org/847f/819a4ea14bd789aca8bc88e85e906cfc657c.pdf
- "Fluid Simulation for Dummies" by Mike Ash
  https://mikeash.com/pyblog/fluid-simulation-for-dummies.html
- "But How DO Fluid Simulations Work?" by Gonkee
  https://www.youtube.com/watch?v=qsYE1wMEMPA
- "Coding Challenge #132: Fluid Simulation" by Daniel Shiffman
  https://www.youtube.com/watch?v=alhpH6ECFvQ
  https://github.com/CodingTrain/website/tree/master/CodingChallenges/CC_132_FluidSimulation/Processing/CC_132_FluidSimulation
"""

import os
import sys
import time
import random
import itertools as it
import ctypes as ct
import matplotlib.cm as cm
import numpy as np


# Engine parameters
GRID_SIZE = 46+2         # Grid size with boundaries around fluid
SOLVER_ITERATIONS = 4
BND_NONE = 0
BND_VERTICAL = 1
BND_HORIZONTAL = 2


# Screen parameters
NUM_OF_COLORS = 254
SPARE_FOR_DEFAULT_COLORS = 2
X_SHIFT = 0
Y_SHIFT = 0
LOWER_HALF_BLOCK = u'\u2584'

# Debug parameters
# DEBUG = open('/dev/pts/1', 'w')


def main():
    if 'DEBUG' in globals():
        sys.stderr = DEBUG
    random.seed(81227)

    screen = Screen(colormap=cm.viridis, mode='matplotlib')
    # screen = Screen(colormap=cm.viridis, mode='green')

    fluid = Fluid(diffusion=0.001, viscosity=0.0001)
    fluid.add_density(x=GRID_SIZE//2, y=GRID_SIZE-2, amount=200)

    # Print aquarium borders
    render_aquarium_borders(screen)

    dt = 0.1

    while True:
        tic = time.time()

        burn(fluid)

        # Velocity step
        fluid.swap_velocity()
        diffuse(BND_VERTICAL, fluid.vel_x, fluid.vel_x0, fluid.viscosity, dt)
        diffuse(BND_HORIZONTAL, fluid.vel_y, fluid.vel_y0, fluid.viscosity, dt)

        project(fluid.vel_x, fluid.vel_y, fluid.vel_x0, fluid.vel_y0)

        fluid.swap_velocity()
        advect(BND_VERTICAL, fluid.vel_x, fluid.vel_x0, fluid.vel_x0, fluid.vel_y0, dt)
        advect(BND_HORIZONTAL, fluid.vel_y, fluid.vel_y0, fluid.vel_x0, fluid.vel_y0, dt)

        project(fluid.vel_x, fluid.vel_y, fluid.vel_x0, fluid.vel_y0)

        # Density step

        # We try to find the densities which, when diffused backward in time,
        # gives the density we started with.
        # For each grid cell of the latter we trace the cell’s center
        # position backwards through the velocity field.
        fluid.swap_density()
        diffuse(BND_NONE, fluid.density, fluid.density0, fluid.diffusion, dt)
        fluid.swap_density()
        advect(BND_NONE, fluid.density, fluid.density0, fluid.vel_x, fluid.vel_y, dt)

        render_fluid_with_blocks(screen, fluid)
        # render_fluid_with_chars(screen, fluid)

        # Sleep only if extra time left
        delay = max(0, dt - (time.time() - tic))
        time.sleep(delay)

        screen.refresh()

    screen.endwin()


def burn(fluid):
    for _ in range(10):
        y = random.randint(1, GRID_SIZE-2)
        if y > GRID_SIZE//2:
            x = random.randint(GRID_SIZE//2 - 5, GRID_SIZE//2 + 5)
            vel_x = random.uniform(-5, 5)
            vel_y = random.uniform(-3, -4)
        else:
            x = random.randint(1, GRID_SIZE-2)
            vel_x = random.uniform(-2, 9)
            vel_y = random.uniform(-4, 2)
        fluid.add_velocity(x, y, vel_x, vel_y)

    fluid.add_density(x=GRID_SIZE//2, y=GRID_SIZE-2, amount=random.randint(5, 18))


def plog(*args, **kwargs):
    """print replacement for logging on other console."""
    if 'DEBUG' in globals():
        print(*args, file=DEBUG)


class Screen:
    # As in Python curses
    A_NORMAL = 0

    def __init__(self, colormap, mode='matplotlib'):
        self._ncurses = ct.CDLL('libncursesw.so.6')
        self._setup_ncurses()
        if mode == 'matplotlib':
            self._init_matplotlib_colors(colormap)
        elif mode == 'green':
            self._init_green_colors()
        else:
            raise Exception('Unknown mode: ', mode)
        self._init_text_colors()

    def _setup_ncurses(self):
        """Setup ncurses screen."""
        self._win = self._ncurses.initscr()
        self._ncurses.start_color()
        self._ncurses.halfdelay(5)
        self._ncurses.noecho()
        self._ncurses.curs_set(0)
        # This fail sometimes
        # self.LINES, self.COLS = self._getmaxyx()

    def _getmaxyx(self):
        """Determine max screen size."""
        plog("self._ncurses.stdscr", self._ncurses.stdscr)
        plog("self._win", self._win)

        # y = self._ncurses.getmaxy(self._win)
        y = self._ncurses.getmaxy(self._ncurses.stdscr)
        # x = self._ncurses.getmaxx(self._win)
        x = self._ncurses.getmaxx(self._ncurses.stdscr)

        plog("LINES, COLS:", (y, x-1))
        return y, x-1

    def _init_green_colors(self):
        """Initialize green color."""
        for color_num in range(NUM_OF_COLORS):
            g = color_num/NUM_OF_COLORS
            ret = self._ncurses.init_extended_color(color_num, 0, int(g*1000), 0)
            if ret != 0:
                plog('init_extended_color error: %d, for color_num: %d' % (ret, color_num))
                raise RuntimeError

        self._init_color_pairs()

    def _init_matplotlib_colors(self, colormap):
        """Initialize color based on matplotlib colormap."""
        assert colormap.N == NUM_OF_COLORS + SPARE_FOR_DEFAULT_COLORS, "We cant initialize more than 256*256 pairs"

        for color_num in range(NUM_OF_COLORS):
            r, g, b = colormap.colors[color_num]
            ret = self._ncurses.init_extended_color(color_num, int(r*1000), int(g*1000), int(b*1000))
            if ret != 0:
                plog('init_extended_color error: %d, for color_num: %d' % (ret, color_num))
                raise RuntimeError

        self._init_color_pairs()

    def _init_color_pairs(self):
        """Initialize color pairs."""
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
        self.diffusion = diffusion  # dyfuzja
        self.viscosity = viscosity  # lepkość

        self.density = np.zeros(shape=(GRID_SIZE, GRID_SIZE))
        self.density0 = np.zeros(shape=(GRID_SIZE, GRID_SIZE))  # previous density

        self.vel_x = np.zeros(shape=(GRID_SIZE, GRID_SIZE))
        self.vel_x0 = np.zeros(shape=(GRID_SIZE, GRID_SIZE))    # previous velocity

        self.vel_y = np.zeros(shape=(GRID_SIZE, GRID_SIZE))
        self.vel_y0 = np.zeros(shape=(GRID_SIZE, GRID_SIZE))    # previous velocity

    def add_density(self, x, y, amount):
        self.density[y, x] += amount

    def add_velocity(self, x, y, vel_x, vel_y):
        self.vel_x[y, x] += vel_x
        self.vel_y[y, x] += vel_y

    def swap_velocity(self):
        self.vel_x0, self.vel_x = self.vel_x, self.vel_x0
        self.vel_y0, self.vel_y = self.vel_y, self.vel_y0

    def swap_density(self):
        self.density0, self.density = self.density, self.density0


def render_fluid_with_blocks(screen, fluid):
    """Render fluid."""
    # Normalize density array
    norm_dens = fluid.density * 50
    # Set max possible color
    norm_dens[norm_dens>=NUM_OF_COLORS] = NUM_OF_COLORS - 1
    norm_dens = norm_dens.astype(int)

    y_shift = Y_SHIFT + 1
    x_shift = GRID_SIZE + X_SHIFT + 1

    # Print debug info
    bg, fg = norm_dens[1:3, 1]
    pair_num = screen.colors_to_pair_num(fg, bg)
    screen.addstr(0 + y_shift, 0 + x_shift, LOWER_HALF_BLOCK, pair_num)
    screen.addstr(0 + y_shift, 3 + x_shift, 'bg: %d fg: %d pair_num: %d  ' % (bg, fg, pair_num))

    vel = (fluid.vel_y[GRID_SIZE//2][GRID_SIZE//2], fluid.vel_x[GRID_SIZE//2][GRID_SIZE//2])
    screen.addstr(1 + y_shift, 0 + x_shift, 'velocity[y, x]: (%4.2f, %4.2f)  ' % vel)

    screen.addstr(2 + y_shift, 0 + x_shift, 'Max     : %6.4f      ' % np.max(fluid.density))
    screen.addstr(3 + y_shift, 0 + x_shift, 'Max norm: %d  ' % np.max(norm_dens))
    screen.addstr(4 + y_shift, 0 + x_shift, 'Min     : %6.4f      ' %  np.min(fluid.density))
    screen.addstr(5 + y_shift, 0 + x_shift, 'Min norm: %d  ' % np.min(norm_dens))

    # Print fluid
    x_shift = X_SHIFT + 1

    for i in range(1, GRID_SIZE-1):
        for j in range(1, GRID_SIZE-1, 2):
            bg, fg = norm_dens[j:j+2, i]
            pair_num = screen.colors_to_pair_num(fg, bg)
            screen.addstr(j//2 + y_shift, (i - 1) + x_shift, LOWER_HALF_BLOCK, pair_num)


def render_fluid_with_chars(screen, fluid):
    """Render fluid using chars."""
    # Normalize density array
    norm_dens = fluid.density * 40
    # Set max possible color
    norm_dens[norm_dens>=NUM_OF_COLORS] = NUM_OF_COLORS - 1
    norm_dens = norm_dens.astype(int)

    y_shift = Y_SHIFT + 1
    x_shift = GRID_SIZE + X_SHIFT + 1

    # Print debug info
    bg, fg = norm_dens[1:3, 1]
    pair_num = screen.colors_to_pair_num(fg, bg)
    screen.addstr(0 + y_shift, 0 + x_shift, LOWER_HALF_BLOCK, pair_num)
    screen.addstr(0 + y_shift, 3 + x_shift, 'bg: %d fg: %d pair_num: %d  ' % (bg, fg, pair_num))

    vel = (fluid.vel_y[GRID_SIZE//2][GRID_SIZE//2], fluid.vel_x[GRID_SIZE//2][GRID_SIZE//2])
    screen.addstr(1 + y_shift, 0 + x_shift, 'velocity[y, x]: (%4.2f, %4.2f)  ' % vel)

    screen.addstr(2 + y_shift, 0 + x_shift, 'Max     : %6.4f      ' % np.max(fluid.density))
    screen.addstr(3 + y_shift, 0 + x_shift, 'Max norm: %d  ' % np.max(norm_dens))
    screen.addstr(4 + y_shift, 0 + x_shift, 'Min     : %6.4f      ' %  np.min(fluid.density))
    screen.addstr(5 + y_shift, 0 + x_shift, 'Min norm: %d  ' % np.min(norm_dens))

    # Print fluid
    x_shift = X_SHIFT + 1

    for i in range(1, GRID_SIZE-1):
        for j in range(1, GRID_SIZE-1, 2):
            bg, _ = norm_dens[j:j+2, i]

            # Golden ratio thresholds
            if bg < 97:
                pair_num = screen.colors_to_pair_num(1, 12 * bg/97)
                screen.addstr(j//2 + y_shift, (i - 1) + x_shift, ' ', pair_num)
            elif bg < 158:
                pair_num = screen.colors_to_pair_num(bg, 24 * bg/158)
                screen.addstr(j//2 + y_shift, (i - 1) + x_shift, '.', pair_num)
            elif bg < 195:
                pair_num = screen.colors_to_pair_num(bg, 36 * bg/195)
                screen.addstr(j//2 + y_shift, (i - 1) + x_shift, '-', pair_num)
            elif bg < 218:
                pair_num = screen.colors_to_pair_num(bg, 48 * bg/218)
                screen.addstr(j//2 + y_shift, (i - 1) + x_shift, 'o', pair_num)
            elif bg < 232:
                pair_num = screen.colors_to_pair_num(bg, 60 * bg/232)
                screen.addstr(j//2 + y_shift, (i - 1) + x_shift, 'X', pair_num)
            elif bg < 241:
                pair_num = screen.colors_to_pair_num(bg, 72 * bg/241)
                screen.addstr(j//2 + y_shift, (i - 1) + x_shift, '%', pair_num)
            else:
                pair_num = screen.colors_to_pair_num(bg, 84 * bg/256)
                screen.addstr(j//2 + y_shift, (i - 1) + x_shift, '@', pair_num)


def render_aquarium_borders(screen):
    """Render aquarium borders."""
    vertical_border = '+' + '-' * (GRID_SIZE-2) + '+'
    screen.addstr(0 + Y_SHIFT, 0 + X_SHIFT, vertical_border)
    screen.addstr((GRID_SIZE-2)//2 + 1 + Y_SHIFT, 0 + X_SHIFT, vertical_border)

    for y in range((GRID_SIZE-2)//2):
        screen.addstr(y + 1 + Y_SHIFT, 0 + X_SHIFT, '|')
        screen.addstr(y + 1 + Y_SHIFT, (GRID_SIZE - 2) + 1 + X_SHIFT, '|')


def diffuse(boundary, x, x0, diffusion, dt):
    """
    Diffusion is the net movement of anything (for example dye) from
    a region of higher concentration to a region of lower concentration.
    """
    a = dt * diffusion * (GRID_SIZE - 2) * (GRID_SIZE - 2)
    linear_solver(boundary, x, x0, a, 1 + 4 * a)


def linear_solver(boundary, x, x0, a, c):
    """
    Solving a system of linear differential equation using Gauss-Seidel
    relaxation.
    """
    for _ in range(SOLVER_ITERATIONS):
        for j in range(1, GRID_SIZE - 1):
            for i in range(1, GRID_SIZE - 1):
                x[j, i] = (x0[j, i] + a*(x[j, i+1] + x[j, i-1] + x[j+1, i] + x[j-1, i])) / c

    set_boundary(boundary, x)


def project(vel_x, vel_y, p, div):
    """
    Forces the velocity to be mass conserving.

    Keep all cells in equilibrium. For incompressible fluids amount of fluid
    in each cell has to stay constant. Amount of fluid going in has must be
    equal to the amount of fluid going out of cell.
    """
    cell_size = 1 / (GRID_SIZE - 2)
    for j in range(1, GRID_SIZE - 1):
        for i in range(1, GRID_SIZE - 1):
            div[j, i] = -0.5 * cell_size * (vel_x[j, i+1] - vel_x[j, i-1] + vel_y[j+1, i] - vel_y[j-1, i])
            p[j, i] = 0

    set_boundary(BND_NONE, div)
    set_boundary(BND_NONE, p)
    linear_solver(0, p, div, 1, 4)

    for j in range(1, GRID_SIZE - 1):
        for i in range(1, GRID_SIZE - 1):
            vel_x[j, i] -= 0.5 * (p[j, i+1] - p[j, i-1]) / cell_size
            vel_y[j, i] -= 0.5 * (p[j+1, i] - p[j-1, i]) / cell_size

    set_boundary(BND_VERTICAL, vel_x)
    set_boundary(BND_HORIZONTAL, vel_y)


def advect(boundary, d, d0, vel_x, vel_y, dt):
    """
    Advection is the transport of a substance or quantity by fluid in this way
    that velocity of transported substance is equal to velocity of fluid.
    """
    dt0 = dt * (GRID_SIZE - 2)

    for j in range(1, GRID_SIZE - 1):
        for i in range(1, GRID_SIZE - 1):
            x = i - dt0 * vel_x[j, i]
            y = j - dt0 * vel_y[j, i]

            if x < 0.5:
                x = 0.5
            elif x > (GRID_SIZE - 2) + 0.5:
                x = (GRID_SIZE - 2) + 0.5
            i0 = int(x)
            i1 = i0 + 1

            if y < 0.5:
                y = 0.5
            elif y > (GRID_SIZE - 2) + 0.5:
                y = (GRID_SIZE - 2) + 0.5
            j0 = int(y)
            j1 = j0 + 1

            s1 = x - i0
            s0 = 1 - s1
            t1 = y - j0
            t0 = 1 - t1

            d[j, i] = s0 * (t0 * d0[j0, i0] + t1 * d0[j1, i0]) + \
                      s1 * (t0 * d0[j0, i1] + t1 * d0[j1, i1])

    set_boundary(boundary, d)


def set_boundary(boundary, matrix):
    """
    Keep fluid from leaking out of the box. Every velocity in the layer next to
    this outer layer is mirrored.
    """
    for i in range(1, GRID_SIZE-1):
        # Copy and mirror value from border - protection against leaking
        if boundary == BND_HORIZONTAL:
            matrix[0, i]           = -matrix[1, i]
            matrix[GRID_SIZE-1, i] = -matrix[GRID_SIZE-2, i]
        # Copy from border
        else:
            matrix[0, i]           = matrix[1, i]
            matrix[GRID_SIZE-1, i] = matrix[GRID_SIZE-2, i]

    for j in range(1, GRID_SIZE-1):
        # Copy and mirror value from border - protection against leaking
        if boundary == BND_VERTICAL:
            matrix[j, 0]           = -matrix[j, 1]
            matrix[j, GRID_SIZE-1] = -matrix[j, GRID_SIZE-2]
        # Copy from border
        else:
            matrix[j, 0]           = matrix[j, 1]
            matrix[j, GRID_SIZE-1] = matrix[j, GRID_SIZE-2]

    # Corners
    matrix[0, 0]                     = 0.5 * (matrix[0, 1] + matrix[1, 0])
    matrix[GRID_SIZE-1, 0]           = 0.5 * (matrix[GRID_SIZE-1, 1] + matrix[GRID_SIZE-2, 0])
    matrix[0, GRID_SIZE-1]           = 0.5 * (matrix[0, GRID_SIZE-2] + matrix[1, GRID_SIZE-1])
    matrix[GRID_SIZE-1, GRID_SIZE-1] = 0.5 * (matrix[GRID_SIZE-1, GRID_SIZE-2] + matrix[GRID_SIZE-2, GRID_SIZE-1])


if __name__ == '__main__':
    main()
