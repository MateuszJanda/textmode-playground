import matplotlib.pyplot as plt
import matplotlib.cm as cm
# from scipy import signal
from scipy.io import wavfile
# import numpy as np

# https://pl.wikipedia.org/wiki/Spektrogram

# https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html
# sample_rate ilość próbek na sekunde
# samples - dla 32-bit PCM, będą to liczby w zakresie [-2147483648, 2147483647]
sample_rate, samples = wavfile.read('out.wav')
print('Rate:', sample_rate)
print('Shape:', samples.shape)
print('Time:', samples.shape[0]/sample_rate, '[sec]') # seconds
# for s in samples:
#     print(s)

# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html
# frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
# print(frequencies.shape)
# print(times.shape)
# print(spectrogram.shape)
# for x in frequencies:
#     print(x)

# plt.plasma()

print('Inferno colors data:')
print(type(cm.inferno))
print(dir(cm.inferno))
print(cm.inferno.N)


# for k, v in cm.inferno.item():
    # print(k, v)
print('Inferno colors:', len(cm.inferno.colors)) # of RGB


# plt.pcolormesh(times, frequencies, 10 * np.log10(spectrogram), animated=True)
# plt.pcolormesh(times, frequencies, spectrogram, animated=True)




# plt.imshow(spectrogram, cmap=cm.plasma)
plt.specgram(samples, Fs=sample_rate, cmap=cm.inferno)
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.show()


# x = np.cumsum(np.random.random(1000) - 0.5)

# print(samples.shape)
# print(type(samples))
# print((spectrogram.shape))

# fig, (ax1, ax2) = plt.subplots(nrows=2)
# data, freqs, bins, im = ax1.specgram(x)
# ax1.axis('tight')

# # "specgram" actually plots 10 * log10(data)...
# ax2.pcolormesh(bins, freqs, 10 * np.log10(data))
# ax2.axis('tight')

# plt.show()