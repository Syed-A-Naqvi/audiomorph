import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy

import librosa
import soundfile as sf
import IPython.display as ipd

import sys

import math



# RAVDESS AVERAGE POWER LEVEL
RAVDESS_P_AVG = 0.0008270979304005066

# saving path to rain audio
rain_noise = "./rainfall.mp3"

# signal plotting function
def plot_signal(signal, sample_rate, plot_title = "Audio Signal", spect=False):
    
    if spect == False:
        df = pd.DataFrame({
            'signals' : signal,
            'seconds' : [i/sample_rate for i in range(0, len(signal))]
        })
        df.plot(y="signals", x="seconds", figsize=(15,5), lw=0.1, title=plot_title, xlabel="seconds", ylabel="amplitude")
        plt.show()
    else:
        gram = librosa.amplitude_to_db(np.abs(librosa.stft(signal)), ref=np.max)
        plt.figure(figsize=(14, 5))
        librosa.display.specshow(gram, sr=sample_rate, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title(plot_title)
        plt.show()
        

# White noise generation function
def generate_white_noise_uniform(length):
    return np.random.uniform(-1,1,length)

# Normal/Gaussian white noise generation function
def generate_white_noise_normal(length):
    return np.random.normal(0, 0.5, length)


def add_noise(noise_type, signal, snr=1):
    
    digital_signal = copy.deepcopy(signal[0])
    sample_rate = signal[1]
    signal_len = len(digital_signal)
    
    if noise_type == 'u':
        noise = generate_white_noise_uniform(signal_len)
    elif noise_type == 'n':
        noise = generate_white_noise_normal(signal_len)
    else:
        noise, _ = librosa.load(rain_noise, sr=None, mono =True)
        start = len(noise)//6
        end = start + signal_len
        noise = np.array(noise[start:end])
    
    # scaling noise down to RAVDESS overall average power level
    # noise_avgpwr_scale = math.sqrt( (RAVDESS_P_AVG*signal_len) / sum(noise**2))
    # noise *= noise_avgpwr_scale
    
    # if (snr >= 0):
    #     scale_factor = math.sqrt( (10**(-snr/10)) )
    #     noise *= scale_factor
    #     print(f'snr = {snr}, scale factor = {scale_factor}, scaling noise')
    # else:
    #     scale_factor = math.sqrt( (10**(snr/10)) )    
    #     digital_signal *= scale_factor
    #     print(f'snr = {snr}, scale factor = {scale_factor}, scaling signal')

    
    
    print(f"noise power level = {sum(noise**2)/len(noise)}")
    print(f"signal power level = {sum(digital_signal**2)/signal_len}")

    noisy_audio = noise + digital_signal
        
    return [noisy_audio, sample_rate]



# requesting information from user
path = str(input("Please enter path to audio file: "))
noise_type = input("Enter \"n\" to add gaussian white noise (mean=0, stdev=0.5), \"u\" to add uniform white noise or \"r\" to add rain noise: ")

# requesting desired noise percentage
    # noise not audible at 55dB snr
    # signal not audible at -30dB snr
    # dB range is thus 55 - (-30) = 85 
    # so 0% noise should be 55 - (0 * 85)
    # and say 30% noise should be 55 - (0.3 * 85)
# percentage = float(input("Enter a noise percentage. 0 means the audio will have no added noise, 100 means the audio will be entirely noise: "))/100
# snr = 55 - (percentage * 85)

snr = float(input("Enter desired snr: "))


# loading audio file
signal, sample_rate = librosa.load(path, sr=None, mono=True)

testfile = [signal,sample_rate]

# plotting original audio
plot_signal(signal,sample_rate, "Original Audio", spect=True)
sf.write("./output/original_audio.wav", testfile[0], testfile[1])

# scaling audio file
scale_factor = math.sqrt( (RAVDESS_P_AVG*len(testfile[0])) / (sum(testfile[0]**2)) )
testfile[0] *= scale_factor

# plotting scaled audio
plot_signal(testfile[0],testfile[1], "Scaled Audio", spect=True)
sf.write("./output/scaled_audio.wav", testfile[0], testfile[1])

# adding noise
noisy_audio = add_noise(noise_type, testfile, snr=snr)    
plot_signal(noisy_audio[0], noisy_audio[1], "Noisy Audio Signal", spect=True)
sf.write("./output/noisy_audio.wav", noisy_audio[0], noisy_audio[1])
