#!/usr/bin/env python3

import locale
import sys
import itertools as it
import ctypes as ct
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy import signal
from scipy.io import wavfile
import numpy as np


TELEMETRY_MODE = False
BLACK = 0


def main():
    # https://pl.wikipedia.org/wiki/Spektrogram
    setup(telemetry=True, terminal='/dev/pts/1')

    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html
    # sample_rate - samples per second
    # samples - for 32-bit PCM, values are in range [-2147483648, 2147483647]
    sample_rate, samples = wavfile.read('out.wav')
    log('Rate:', sample_rate)
    log('Shape:', samples.shape)
    log('Time:', samples.shape[0]/sample_rate, '[sec]')

    # sci_spectogram(samples, sample_rate)
    # plt_spectogram(samples, sample_rate)
    # plt.show()

    log('Inferno colors data:')
    log(type(cm.inferno))
    log(dir(cm.inferno))
    log(cm.inferno.N)
    log('Inferno colors:', len(cm.inferno.colors))  # of RGB

    screen = Screen()
    # screen.render()
    screen._print(1, 0, 67, 'a')
    screen._print(2, 0, 257, 'b')
    screen._print(3, 0, 3567, 'c')
    screen._print(4, 0, 32994, 'd')
    screen._ncurses.refresh()

    while True:
        pass

    screen.endwin()


def setup(telemetry=False, terminal='/dev/pts/1'):
    """Main setup function."""
    setup_telemetry(telemetry, terminal)


def setup_telemetry(telemetry=False, terminal='/dev/pts/1'):
    """
    Redirect stderr to other terminal. Run tty command, to get terminal id.

    $ tty
    /dev/pts/1
    """
    global TELEMETRY_MODE
    TELEMETRY_MODE = telemetry
    if TELEMETRY_MODE:
        sys.stderr = open(terminal, 'w')


def log(*args, **kwargs):
    """log on stderr."""
    if TELEMETRY_MODE:
        print(*args, file=sys.stderr)


def sci_spectogram(samples, sample_rate):
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html
    frequencies, times, spectrogram = signal.spectrogram(samples, fs=sample_rate, nfft=1028)
    log('frequencies.shape', frequencies.shape)
    log('times.shape', times.shape)
    log('spectrogram.shape', spectrogram.shape)
    log('spectrogram value', 10*np.log10(spectrogram[0][1]))

    plt.figure(2)
    plt.pcolormesh(times, frequencies, 10*np.log10(spectrogram), cmap=cm.inferno)
    plt.title('signal spectrogram')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')


def plt_spectogram(samples, sample_rate):
    plt.figure(3)
    plt.specgram(samples, Fs=sample_rate, cmap=cm.inferno, NFFT=1028)
    plt.title('matplotlib sectrogram')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')


# Macros and definitions from curses.h
NCURSES_ATTR_SHIFT = 8


def NCURSES_BITS(mask, shift):
    return mask << (shift + NCURSES_ATTR_SHIFT)


A_COLOR = NCURSES_BITS((1 << 8) - 1, 0)
A_NORMAL = 0


# def COLOR_PAIR(self._ncurses):
#     return NCURSES_BITS(self._ncurses, 0) & A_COLOR


class Screen:
    def __init__(self):
        self._ncurses = ct.CDLL('libncursesw_g.so.6.1')

        # if not self._ncurses.can_change_color():
        #     log('Color change not supported in this terminal!')
        #     exit()

        self._setup_ncurses()
        self._init_colors()

        self._buf = np.ones(shape=(self.LINES*2, self.COLS-1), dtype=np.int32)

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
       return y, x

    def _init_colors(self):
        for color_num in range(cm.inferno.N):
            r, g, b = cm.inferno.colors[color_num]
            ret = self._ncurses.init_extended_color(color_num, int(r*1000), int(g*1000), int(b*1000))
            if ret != 0:
                log('init_extended_color error: %d, for color_num: %d' % (ret, color_num))
                raise RuntimeError

        for bg, fg in it.product(range(cm.inferno.N), range(cm.inferno.N)):
            pair_num = bg * cm.inferno.N + fg

            if pair_num == 0:
                continue

            ret = self._ncurses.init_extended_pair(pair_num, fg, bg)
            if ret != 0:
                log('init_extended_pair error: %d, for pair_num: %d' % (ret, pair_num))
                raise RuntimeError

    def _init_colors_basic(self):
        r, g, b = 0.99, 0.21, 0.17
        color_num1 = 1
        ret = self._ncurses.init_extended_color(color_num1, int(r*1000), int(g*1000), int(b*1000))
        if ret != 0:
            log('init_extended_color error: %d, for color_num: %d' % (ret, color_num))
            raise RuntimeError

        r, g, b = 0.32, 0.01, 0.73
        color_num2 = 2
        ret = self._ncurses.init_extended_color(color_num2, int(r*1000), int(g*1000), int(b*1000))
        if ret != 0:
            log('init_extended_color error: %d, for color_num: %d' % (ret, color_num))
            raise RuntimeError

        pair_num = 1
        ret = self._ncurses.init_extended_pair(pair_num, color_num1, color_num2)
        if ret != 0:
            log('init_extended_pair error: %d, for pair_num: %d' % (ret, pair_num))
            raise RuntimeError

    def draw_point(self, pos, color):
        # Don't draw point when they are out of the screen
        if not (0 <= pos[1] < self._buf[1] and 0 <= pos[0] < self._buf[0]):
            return

        self._buf[pos[0], pos[1]] = color

    def render(self):
        """Draw buffer content on screen."""
        # https://en.wikipedia.org/wiki/List_of_Unicode_characters#Block_Elements
        LOWER_HALF_BLOCK = u'\u2584'.encode('utf-8')

        for y, x in it.product(range(self.LINES), range(self.COLS-1)):
            bg, fg = self._buf[y*2:y*2+2, x]
            pair_num = bg * cm.inferno.N + fg
            pair_num = 257

            self._print(y, x, pair_num, 'asdf')

        self._ncurses.refresh()
        log('po refresh')

    def _print(self, y, x, pair_num, text):
        pair_num_short = ct.cast((ct.c_int*1)(pair_num), ct.POINTER(ct.c_short)).contents
        pair_num_pt = ct.c_int(pair_num)
        ret = self._ncurses.attr_set(ct.c_int(A_NORMAL), pair_num_short, ct.pointer(pair_num_pt))
        if ret != 0:
            log('attr_set error %d, pair_num: %d' % (ret, pair_num))
            raise RuntimeError

        ret = self._ncurses.mvprintw(y, x, text.encode('utf-8'))
        if ret != 0:
            log('mvprintw error: %d, pair_num: %d' % (ret, pair_num))
            raise RuntimeError

    def endwin(self):
        ch = self._ncurses.getch()
        while ch != ord('q'):
            ch = self._ncurses.getch()
        self._ncurses.endwin()


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    main()
