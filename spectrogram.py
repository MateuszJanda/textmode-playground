#!/usr/bin/env python3

import locale
import sys
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
    screen.refresh()

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


def COLOR_PAIR(n):
    return NCURSES_BITS(n, 0) & A_COLOR


class Screen:
    def __init__(self):
        self._ncurses = ct.CDLL('libncursesw_g.so.6.1')

        # if not self._ncurses.can_change_color():
        #     log('Color change not supported in this terminal!')
        #     exit()

        self._setup_ncurses()
        self._init_colors()

        self.LINES, self.COLS = self._getmaxyx()

        buf_shape = (self.LINES*2, self.COLS-1)
        # self._buf = np.zeros(shape=buf_shape, dtype=np.int32)
        self._buf = np.ones(shape=buf_shape, dtype=np.int32)


    def _setup_ncurses(self):
        """Setup ncurses screen."""
        self._win = self._ncurses.initscr()
        self._ncurses.start_color()
        self._ncurses.halfdelay(5)
        self._ncurses.noecho()
        self._ncurses.curs_set(0)

    def _getmaxyx(self):
       y = self._ncurses.getmaxy(self._win)
       x = self._ncurses.getmaxx(self._win)
       return y, x

    def _init_colors(self):
        for color_num in range(cm.inferno.N):
            r, g, b = cm.inferno.colors[color_num]
            self._ncurses.init_extended_color(color_num, int(r*1000), int(g*1000), int(b*1000))

        for bg in range(cm.inferno.N):
            for fg in range(cm.inferno.N):
                pair_num = bg * cm.inferno.N + fg
                # if pair_num == 0:
                #     continue
                r = self._ncurses.init_extended_pair(pair_num, fg, bg)
                if r < 0:
                    log(r, pair_num)

    def draw_point(self, pos, color):
        # Don't draw point when they are out of the screen
        if not (0 <= pos[1] < self._buf[1] and 0 <= pos[0] < self._buf[0]):
            return

        self._buf[pos[0], pos[1]] = color

    def refresh(self):
        """Draw buffer content on screen."""
        # https://en.wikipedia.org/wiki/List_of_Unicode_characters#Block_Elements
        LOWER_HALF_BLOCK = u'\u2584'.encode('utf-8')

        # self._ncurses.attron(COLOR_PAIR(1))
        # self._ncurses.mvprintw(3, 1, LOWER_HALF_BLOCK)
        # self._ncurses.attroff(COLOR_PAIR(1))

        # pair_num = 5
        # short = ct.cast((ct.c_int*1)(pair_num), ct.POINTER(ct.c_short)).contents
        # i = ct.c_int(pair_num)
        # self._ncurses.attr_set(ct.c_int(A_NORMAL), short, ct.pointer(i))
        self._ncurses.mvprintw(2, 0, 'asdf')

        log('tutaj')
        return

        for y in range(self.LINES):
            for x in range(self.COLS-1):
                bg, fg = self._buf[y*2:y*2+2, x]
                pair_num = bg * cm.inferno.N + fg
                # log(pair_num)
                log(self._buf[y*2:y*2+2, x])
                log(bg)
                log(fg)
                log(pair_num)


                # self._ncurses.attron(COLOR_PAIR(pair_num))
                # self._ncurses.attron(self._ncurses.COLOR_PAIR(pair_num))
                short = ct.cast((ct.c_int*1)(pair_num), ct.POINTER(ct.c_short)).contents
                i = ct.c_int(pair_num)
                self._ncurses.attr_set(ct.c_int(A_NORMAL), short, ct.pointer(i))
                self._ncurses.mvprintw(2, 0, LOWER_HALF_BLOCK)
                # self._ncurses.attroff(COLOR_PAIR(pair_num))

        self._ncurses.refresh()
        log('po refresh')

    def endwin(self):
        self._ncurses.getch()
        self._ncurses.endwin()


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    main()
