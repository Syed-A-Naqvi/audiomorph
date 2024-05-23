import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import librosa
import soundfile as sf
import IPython.display as ipd

import sys

import math



# RAVDESS AVERAGE POWER LEVEL
RAVDESS_P_AVG = 0.0008270979304005066

# signal plotting function
def plot_signal(signal, sample_rate, plot_title = "Audio Signal"):
    df = pd.DataFrame({
        'signals' : signal,
        'seconds' : [i/sample_rate for i in range(0, len(signal))]
    })
    df.plot(y="signals", x="seconds",
            figsize=(15,5), lw=0.1,
            title=plot_title, xlabel="seconds", ylabel="amplitude")

# White noise generation function
def generate_white_noise_uniform(length):
    return np.random.uniform(-1,1,length)

# Noise adding function
def add_noise(noise_type, signal, snr=1):
    
    digital_signal = signal[0]
    sample_rate = signal[1]
    signal_len = len(digital_signal)
    signal_power = np.sum(digital_signal**2)/signal_len
    
    if noise_type == 'w':
        noise = generate_white_noise_uniform(signal_len)
    else:
        noise, _ = librosa.load(rain_noise, sr=None, mono =True)
        start = len(noise)//6
        end = start + signal_len
        noise = np.array(noise[start:end])
    
    noise_power = np.sum(noise**2)/signal_len
    noise_scale_factor = math.sqrt( (signal_power/noise_power)*(10**(-snr/10)) )
    
    noise *= noise_scale_factor
    noisy_audio = noise + digital_signal
    
    #normalizing noisy audio
    # scale_factor = math.sqrt(RAVDESS_P_AVG*signal_len/sum(noise**2))
    # noisy_audio *= scale_factor
    
    return [noisy_audio, sample_rate]

# saving path to rain audio
rain_noise = "./rainfall.mp3"

# requesting information from user
path = sys.argv[1]
path = str(path)
noise_type = input("Enter \"w\" to add white noise. Enter \"r\" to add rain noise.")
snr = input("Enter the desired signal to noise ratio (dB) in [-inf,inf]:")
snr = int(snr)

# loading audio file
signal, sample_rate = librosa.load(path, sr=None, mono=True)

testfile = [signal,sample_rate]

# plotting original audio
plot_signal(signal,sample_rate, "Original Audio")
plt.show()
sf.write("./output/original_audio.wav", testfile[0], testfile[1])

# scaling audio file
scale_factor = math.sqrt( (RAVDESS_P_AVG*len(testfile[0])) / (sum(testfile[0]**2)) )
testfile[0] *= scale_factor

# plotting scaled audio
plot_signal(testfile[0],testfile[1], "Scaled Audio")
plt.show()
sf.write("./output/scaled_audio.wav", testfile[0], testfile[1])

# adding noise
noisy_audio = add_noise(noise_type, testfile, snr=snr)    
plot_signal(noisy_audio[0], noisy_audio[1], "Noisy Audio Signal")
plt.show()
sf.write("./output/noisy_audio.wav", noisy_audio[0], noisy_audio[1])
