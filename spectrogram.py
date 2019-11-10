#!/usr/bin/env python3

"""
Author: Mateusz Janda <mateusz janda at gmail com>
Site: github.com/MateuszJanda
Ad maiorem Dei gloriam
"""

import sys
import itertools as it
import ctypes as ct
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy import signal
from scipy.io import wavfile
import numpy as np


DEBUG = False


def main():
    # https://pl.wikipedia.org/wiki/Spektrogram
    # setup_stderr(terminal='/dev/pts/1')

    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html
    # sample_rate - samples per second
    # samples - for 32-bit PCM, values are in range [-2147483648, 2147483647]
    sample_rate, samples = wavfile.read('out.wav')
    log('Rate:', sample_rate)
    log('Shape:', samples.shape)
    log('Time:', samples.shape[0]/sample_rate, '[sec]')

    log('Inferno colors:', cm.inferno.N)  # of RGB

    # sci_spectogram(samples, sample_rate)
    # plt_spectogram(samples, sample_rate)
    # plt.show()

    screen = Screen()
    screen.render(samples, sample_rate)
    screen.endwin()


def setup_stderr(terminal='/dev/pts/1'):
    """
    Redirect stderr to other terminal. Run tty command, to get terminal id.

    $ tty
    /dev/pts/1
    """
    if DEBUG:
        sys.stderr = open(terminal, 'w')


def log(*args, **kwargs):
    """log on stderr."""
    if DEBUG:
        print(*args, file=sys.stderr)


def sci_spectogram(samples, sample_rate):
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html
    frequencies, times, spectrogram = signal.spectrogram(samples, fs=sample_rate, nfft=1024)
    log('frequencies.shape', frequencies.shape)
    log('times.shape', times.shape)
    log('spectrogram.shape', spectrogram.shape)

    plt.figure(2)
    plt.pcolormesh(times, frequencies, 10*np.log10(spectrogram), cmap=cm.inferno)
    plt.title('signal spectrogram')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')


def plt_spectogram(samples, sample_rate):
    plt.figure(3)
    plt.specgram(samples, Fs=sample_rate, cmap=cm.inferno, NFFT=1024)
    plt.title('matplotlib sectrogram')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')


class Screen:
    A_NORMAL = 0
    # https://en.wikipedia.org/wiki/List_of_Unicode_characters#Block_Elements
    LOWER_HALF_BLOCK = u'\u2584'

    def __init__(self):
        self._ncurses = ct.CDLL('./libncursesw_g.so.6.1')
        self._setup_ncurses()
        self._init_colors()

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

    def _init_colors(self):
        for color_num in range(cm.inferno.N):
            r, g, b = cm.inferno.colors[color_num]
            ret = self._ncurses.init_extended_color(color_num, int(r*1000), int(g*1000), int(b*1000))
            if ret != 0:
                log('init_extended_color error: %d, for color_num: %d' % (ret, color_num))
                raise RuntimeError

        assert cm.inferno.N == 256

        for bg, fg in it.product(range(cm.inferno.N), range(cm.inferno.N)):
            pair_num = bg * cm.inferno.N + fg

            if pair_num == 0:
                continue

            ret = self._ncurses.init_extended_pair(pair_num, fg, bg)
            if ret != 0:
                log('init_extended_pair error: %d, for pair_num: %d' % (ret, pair_num))
                raise RuntimeError

    def render(self, samples, sample_rate):
        """Draw buffer content on screen."""
        spectrogram = self._spectogram(samples, sample_rate)

        for shift in range(spectrogram.shape[1] - self.COLS):
            for y, x in it.product(range(self.LINES), range(self.COLS)):
                bg, fg = spectrogram[y*2:y*2+2, x+shift]
                pair_num = int(bg) * cm.inferno.N + int(fg)

                self.print(y, x, pair_num, Screen.LOWER_HALF_BLOCK)

            self.refresh()

    def _spectogram(self, samples, sample_rate):
        _, _, spectrogram = signal.spectrogram(samples, fs=sample_rate, nfft=1024)
        spectrogram = 10*np.log10(spectrogram)

        # Normalize data
        shift = 0 - spectrogram.min()
        spectrogram = spectrogram + shift
        spectrogram = (spectrogram * cm.inferno.N) / spectrogram.max()

        # Flip array
        np.flip(spectrogram, axis=1)

        # Cut few last rows - they don't fit on screen
        lines_per_block = spectrogram.shape[0] // (self.LINES * 2)
        last_row = (self.LINES * 2) * lines_per_block
        spectrogram = spectrogram[:last_row, :]

        # Reduce size of rows in array (calculate mean value for each group)
        spectrogram = spectrogram.transpose().reshape(-1, lines_per_block).mean(1) \
            .reshape(spectrogram.shape[1], spectrogram.shape[0]//lines_per_block).transpose()

        return spectrogram

    def print(self, y, x, pair_num, text):
        pair_num_short = ct.cast((ct.c_int*1)(pair_num), ct.POINTER(ct.c_short)).contents
        pair_num_pt = ct.c_int(pair_num)
        ret = self._ncurses.attr_set(ct.c_int(self.A_NORMAL), pair_num_short, ct.pointer(pair_num_pt))
        if ret != 0:
            log('attr_set error %d, pair_num: %d' % (ret, pair_num))
            raise RuntimeError

        ret = self._ncurses.mvprintw(y, x, text.encode('utf-8'))
        if ret != 0:
            log('mvprintw error: %d, y: %d, x: %d, pair_num: %d' % (ret, y, x, pair_num))
            raise RuntimeError

    def refresh(self):
        self._ncurses.refresh()

    def endwin(self):
        ch = self._ncurses.getch()
        while ch != ord('q'):
            ch = self._ncurses.getch()
        self._ncurses.endwin()

        log('The end.')


if __name__ == '__main__':
    main()
