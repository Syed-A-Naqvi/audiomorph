import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy
import soundfile as sf
import scipy.signal as signal
import librosa

import mpmath as m
# setting mpmath precision
m.mp.dps = 20


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
cutoff_freq = 128  # Cutoff frequency in Hz
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
        ax = df.plot(y="signals", x="seconds", figsize=(15,5), lw=0.1, title=plot_title, xlabel="seconds", ylabel="amplitude")
        fig = ax.get_figure()
        fig.savefig(save_path+plot_title)
    
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
def add_noise(noise_type, signal, p_or_s, target_avg_power=RAVDESS_P_AVG, percentage_noise=.5, snr=0):
    
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

    if(p_or_s == 'r'):        
        # scaling noise up or down based on desired snr
        snr_scale_factor = np.sqrt( (np.mean(digital_signal**2)/np.mean(noise**2)) * (10**(-snr/10)) )
        noise *= snr_scale_factor
        
        # append scaled noise to original signal
        noisy_audio = noise + digital_signal
        
        # scaling noisy audio back down to RAVDESS average
        rav_avg_scale = np.sqrt( (RAVDESS_P_AVG*signal_len) / sum(noisy_audio**2))
        
        # final noisy audio scale
        noisy_audio *= rav_avg_scale
        
        #scaling noise and digital_signal for power and percentage calculations
        noise *= rav_avg_scale
        digital_signal *= rav_avg_scale
        
        # Power calculations
        P_noise = np.mean(noise**2)
        P_signal = np.mean(digital_signal**2)
        
        # Percentage calculations
        percentage_noise = P_noise/RAVDESS_P_AVG
        percentage_signal = P_signal/RAVDESS_P_AVG
    
    else:
        # Calculating percentage of the final audio that should be signal vs noise
        percentage_signal = 1 - percentage_noise
        
        # Current avg power levels of signal and noise
        P_signal = m.fsum(digital_signal, squared=True)/signal_len
        P_noise = m.fsum(noise, squared=True)/signal_len
        
        # Scaling noise
        noise_scale_factor = m.sqrt( (percentage_noise*target_avg_power)/P_noise )
        noise = [x*noise_scale_factor for x in noise]
        
        # Scaling signal
        signal_scale_factor = m.sqrt( (percentage_signal*target_avg_power)/P_signal )
        digital_signal = [x*signal_scale_factor for x in digital_signal]
                
        # Creating noisy audio
        noisy_audio = [digital_signal[i] + noise[i] for i in range(signal_len)]
        
        # Recalculating avg power levels of signal and noise
        P_signal = m.fsum(digital_signal, squared=True)/signal_len
        P_noise = m.fsum(noise, squared=True)/signal_len

        if(percentage_noise == 1):
            snr = "-inf"
        elif(percentage_noise == 0):
            snr = "inf"
        else:
            snr = float(10*(m.log10(P_signal/P_noise)))
    
    print(f"\n{round(percentage_noise*100,10)}% of the average power of the noisy audio is noise")
    print(f"{round(percentage_signal*100,10)}% of the average power of the noisy audio is signal")
    print(f"Average power of noise = {round(P_noise,10)}")    
    print(f"Average power of signal = {round(P_signal,10)}")
    print(f"Signal-to-Noise ratio (SNR) = {round(snr,10)} dB")
            
    return [np.array(noisy_audio, dtype=float), sample_rate]


############## REQUESTING INFORMATION ##############
# requesting audio file path
path = str(input("Enter path to desired audio file:\n(use custom audio file < 15s or the loud.wav/quiet.wav RAVDESS samples in repo)\n"))

# Requesting noise type
print("\nEnter 'u' for uniform white noise,\n",
      "     'n' for normally distributed white noise\n",
      "     'ro' for unfiltered rain noise\n",
      "     'rf' for filtered rain noise.")
while(1):
    noise_type = input()
    if (noise_type not in set(['rf', 'n', 'u', 'ro'])):
        print("Please enter a valid noise type.")
    else:
        break

# Requesting plot type
print("\nEnter 's' to generate spectrograms,\n",
      "     't' to generate amplitude timeseries:")
while(1):
    plot_type = input()
    
    if (plot_type  == 's'):
        plot_type = True
        break
    elif (plot_type  == 't'):
        plot_type = False
        break
    else:
        print("Please enter a valid plot type.")

print("\nEnter 'p' to add noise as percentage, 'r' to add noise using SNR value:")
while(1):
    proportion_type = input()
    if(proportion_type not in set(['p','r'])):
        print("Please enter either 'p' for percentage or 'r' for snr.")
    else:
        break

# percentage of final audio that should be noise
if(proportion_type == 'p'):
    print("\nEnter the fraction [0,1] of the average power of the final audio that should be noise:")
    while(1):
        percentage_noise = float(input())
        if(percentage_noise>1 or percentage_noise<0):
            print("Please enter a value in [0,1]")
        else:
            break
else:
    print("\nEnter desired signal-to-noise ratio in db (0dB means equal signal-to-noise):")
    snr = float(input())
############## REQUESTING INFORMATION ##############



############## WRITING OUTPUT ##############
# loading audio file
signal, sample_rate = librosa.load(path, sr=None, mono=True)
audio = [signal,sample_rate]

# plotting original audio
plot_signal(audio[0],audio[1], "Original Audio", spect=plot_type)
sf.write("./output/original_audio.wav", audio[0], audio[1])

# scaling audio file
scale_factor = np.sqrt( (RAVDESS_P_AVG*len(audio[0])) / (sum(audio[0]**2)) )
audio[0] *= scale_factor

# plotting scaled audio
plot_signal(audio[0],audio[1], "Scaled Audio", spect=plot_type)
sf.write("./output/scaled_audio.wav", audio[0], audio[1])

# adding noise
if(proportion_type == 'p'):
    noisy_audio = add_noise(noise_type, audio, p_or_s='p', percentage_noise = percentage_noise)
else:
    noisy_audio = add_noise(noise_type, audio, p_or_s='r', snr=snr)

plot_signal(noisy_audio[0], noisy_audio[1], "Noisy Audio ", spect=plot_type)
sf.write("./output/noisy_audio.wav", noisy_audio[0], noisy_audio[1])

print("All plots and audio files have been written to the \'output\' directory in the root folder of the repo.\n")
############## WRITING OUTPUT ##############