#!/usr/bin/env python3

import locale
import curses
import sys
import time
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy import signal
from scipy.io import wavfile
import numpy as np


TELEMETRY_MODE = False
RGB_DIM = 1
BLACK = 0


def main(scr):
    # https://pl.wikipedia.org/wiki/Spektrogram
    setup(scr, telemetry=True, terminal='/dev/pts/2')

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

    screen = Screen(scr)
    log('COLOR_PAIRS', curses.COLOR_PAIRS)
    screen.refresh()

    while not can_exit(scr):
        time.sleep(0.5)


def can_exit(scr):
    """Wait for key (defined by halfdelay), and check if q."""
    ch = scr.getch()
    return ch == ord('q')


def setup(scr, telemetry=False, terminal='/dev/pts/1'):
    """Main setup function."""
    setup_curses(scr)
    setup_telemetry(telemetry, terminal)

    if not curses.can_change_color():
        log('Color change not supported in this terminal!')
        exit()


def setup_curses(scr):
    """Setup curses screen."""
    curses.start_color()
    curses.halfdelay(5)
    curses.noecho()
    curses.curs_set(False)
    scr.clear()


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


class Screen:
    def __init__(self, scr):
        self._scr = scr
        buf_shape = (2*curses.LINES, curses.COLS-1, RGB_DIM)
        self._buf = np.full(shape=buf_shape, fill_value=BLACK)

        self._init_colors()

    def _init_colors(self):
        # curses.init_color(0, 0, 0, 0)
        curses.init_color(1, 0, 999, 0)
        curses.init_color(2, 999, 999, 0)

        # At most curses.COLOR_PAIRS-1
        # curses.init_pair(0, 1, 0)
        curses.init_pair(1, 0, 1)
        curses.init_pair(2, 2, 1)

    def draw_point(self, pos, color):
        # Don't draw point when they are out of the screen
        if not (0 <= pos[1] < self._buf[1] and 0 <= pos[0] < self._buf[0]):
            return

        self._buf[pos[0], pos[1]] = color

    def refresh(self):
        """Draw buffer content to screen."""
        # https://en.wikipedia.org/wiki/List_of_Unicode_characters#Block_Elements
        LOWER_HALF_BLOCK = u'\u2584'

        # for num, line in enumerate(self._buf):
            # self._scr.addstr(num, 0, LOWER_HALF_BLOCK, color)
        self._scr.addstr(0, 0, LOWER_HALF_BLOCK, curses.color_pair(0))
        self._scr.addstr(1, 0, LOWER_HALF_BLOCK, curses.color_pair(1))
        self._scr.addstr(2, 0, LOWER_HALF_BLOCK, curses.color_pair(2))
        self._scr.addstr(3, 0, 'asdf', 2)
        self._scr.refresh()


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
