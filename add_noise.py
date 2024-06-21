import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy
import soundfile as sf
import scipy.signal as signal

from glob import glob

import librosa
import IPython.display as ipd

import math



# RAVDESS AVERAGE POWER LEVEL
RAVDESS_P_AVG = 0.0008270979304005066


# rainfall noise downloaded from https://freesound.org/people/Signov/sounds/166741/
# trimmed at: https://audiotrimmer.com/
# saving path to rain audio
rain_noise_file = "./rainfall-trimmed.flac"
rain_noise_unfiltered, rain_noise_sr = librosa.load(rain_noise_file, sr=None, mono =True)


# High-pass filter
### CHATGPT ###
# Define the cutoff frequency for the high-pass filter
cutoff_freq = 100  # Cutoff frequency in Hz
# Calculate Nyquist frequency
nyquist = 0.5 * rain_noise_sr
# Normalize the cutoff frequency
normal_cutoff = cutoff_freq / nyquist
# Design the high-pass filter
b, a = signal.butter(1, normal_cutoff, btype='high', analog=False)
# Apply the filter
rain_noise_filtered = signal.filtfilt(b, a, rain_noise_unfiltered)
### CHATGPT ###

# signal plotting function
def plot_signal(signal, sample_rate, plot_title = "Audio Signal", spect=False, save_path="./output/"):
    
    if spect == False:
        df = pd.DataFrame({
            'signals' : signal,
            'seconds' : [i/sample_rate for i in range(0, len(signal))]
        })
        df.plot(y="signals", x="seconds", figsize=(15,5), lw=0.1, title=plot_title, xlabel="seconds", ylabel="amplitude")
    
    else:
        gram = librosa.amplitude_to_db(np.abs(librosa.stft(signal)), ref=np.max)
        plt.figure(figsize=(14, 5))
        librosa.display.specshow(gram, sr=sample_rate, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title(plot_title)
        
        if save_path:
            plt.savefig(save_path+plot_title)  # Save the plot to the specified path
        else:
            plt.show()  # Show the plot as before
        

# White noise generation function
def generate_white_noise_uniform(length):
    return np.random.uniform(-1,1,length)

# Normal/Gaussian white noise generation function
def generate_white_noise_normal(length):
    return np.random.normal(0, 0.5, length)


# mixing function
def add_noise(noise_type, signal, snr=0):
    
    digital_signal = copy.deepcopy(signal[0])
    sample_rate = signal[1]
    signal_len = len(digital_signal)

    if noise_type == 'u':
        noise = generate_white_noise_uniform(signal_len)
    elif noise_type == 'n':
        noise = generate_white_noise_normal(signal_len)
    elif noise_type == 'ro':
        noise = np.array(rain_noise_unfiltered[0:signal_len])
    elif noise_type == 'rf':
        noise = np.array(rain_noise_filtered[0:signal_len])
    

    ############################ ALTERNATIVE METHOD ############################
    # scaling noise down to RAVDESS overall average power level
    # noise_avgpwr_scale = math.sqrt( (overall_P_avg*signal_len) / sum(noise**2))
    # noise *= noise_avgpwr_scale
    
    # if (snr >= 0):
    #     scale_factor = math.sqrt( (10**(-snr/10)) )
    #     noise *= scale_factor
    #     print(f'snr = {snr}, scale factor = {scale_factor}, scaling noise')
    # else:
    #     scale_factor = math.sqrt( (10**(snr/10)) )    
    #     digital_signal *= scale_factor
    #     print(f'snr = {snr}, scale factor = {scale_factor}, scaling signal')
    
    # print(f"noise power level = {sum(noise**2)/len(noise)}")
    # print(f"signal power level = {sum(digital_signal**2)/signal_len}")
    ############################ ALTERNATIVE METHOD ############################


    # scaling noise up or down based on desired snr
    snr_scale_factor = math.sqrt( (np.mean(digital_signal**2)/np.mean(noise**2)) * (10**(-snr/10)) )
    noise *= snr_scale_factor
    
    # append scaled noise to original signal
    noisy_audio = noise + digital_signal
    
    # scaling noisy audio back down to RAVDESS average
    rav_avg_scale = math.sqrt( (RAVDESS_P_AVG*signal_len) / sum(noisy_audio**2))
    
    # final noisy audio scale
    noisy_audio *= rav_avg_scale
    
        
    return [noisy_audio, sample_rate]


# requesting information from user
path = str(input("Enter path to audio file: "))
while(1):
    print("Enter 'u' for uniform white noise,\n",
          "     'n' for normally distributed white noise\n",
          "     'ro' for unfiltered rain noise\n",
          "     'rf' for filtered rain noise.")
    noise_type = input()
    
    if (noise_type not in set(['rf', 'n', 'u', 'ro'])):
        print("Please enter a valid noise type.\n")
    else:
        break

# signal to noise ratio in dB
snr = float(input("Enter relative power of signal to noise in dB:"))

# loading audio file
signal, sample_rate = librosa.load(path, sr=None, mono=True)
audio = [signal,sample_rate]

# plotting original audio
plot_signal(audio[0],audio[1], "Original Audio", spect=True)
sf.write("./output/original_audio.wav", audio[0], audio[1])

# scaling audio file
scale_factor = math.sqrt( (RAVDESS_P_AVG*len(audio[0])) / (sum(audio[0]**2)) )
audio[0] *= scale_factor

# plotting scaled audio
plot_signal(audio[0],audio[1], "Scaled Audio", spect=True)
sf.write("./output/scaled_audio.wav", audio[0], audio[1])

# adding noise
noisy_audio = add_noise(noise_type, audio, snr=snr)    
plot_signal(noisy_audio[0], noisy_audio[1], "Noisy Audio Signal", spect=True)
sf.write("./output/noisy_audio.wav", noisy_audio[0], noisy_audio[1])
