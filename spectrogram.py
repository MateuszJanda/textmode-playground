#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy import signal
from scipy.io import wavfile
import numpy as np


def main():
    # https://pl.wikipedia.org/wiki/Spektrogram
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html

    # sample_rate - samples per second
    # samples - for 32-bit PCM, values are in range [-2147483648, 2147483647]
    sample_rate, samples = wavfile.read('out.wav')
    print('Rate:', sample_rate)
    print('Shape:', samples.shape)
    print('Time:', samples.shape[0]/sample_rate, '[sec]')

    sci_spectrogram(samples, sample_rate)
    plt_spectogram(samples, sample_rate)
    plt.show()

    print('Inferno colors data:')
    print(type(cm.inferno))
    print(dir(cm.inferno))
    print(cm.inferno.N)
    print('Inferno colors:', len(cm.inferno.colors))  # of RGB


def sci_spectrogram(samples, sample_rate):
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html
    frequencies, times, spectrogram = signal.spectrogram(samples, fs=sample_rate, nfft=1028)
    print('frequencies.shape', frequencies.shape)
    print('times.shape', times.shape)
    print('spectrogram.shape', spectrogram.shape)
    print('spectrogram value', 10*np.log10(spectrogram[0][1]))

    plt.figure(2)
    # plt.imshow(10*np.log10(spectrogram), aspect='auto', cmap=cm.inferno, origin='lower')
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


if __name__ == '__main__':
    main()
