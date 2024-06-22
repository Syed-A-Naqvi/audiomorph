# Description

The purpose of this project is to obtain granular control over the amount of noise inserted into a sound file. If one specifies a desired signal to noise ratio or noise percentage, the appropriate amount of noise will be inserted. Controlled noise insertion allows for the testing of the effects of noise on audio in various settings.

# Instructions

- clone repo and run command ```python3 add_noise.py``` in the terminal from project root directory
- follow prompts to create the noisy audio and related visualizations
- the provided file is normalized to the RAVDESS average power level and noise is inserted based on the specified signal to noise ratio or noise percentage
- check the output folder for original audio, scaled(normalized) audio, final noisy audio and all related visualizations

- for signal to noise ratio:
  - 0 dB means signal power is the same as noise power
  - -10 dB means noise power is 10 times greater than signal power
  - 10 dB means signal power is 10 times greater than noise power

- for noise as a percentage of the average power of the final noisy audio:
  - 0% means there is no noise, only signal (snr = inf dB)
  - 100% means there is no signal, only noise (snr = -inf dB)
  - 50% means half the final audio is noise, half is signal (snr = 0dB)