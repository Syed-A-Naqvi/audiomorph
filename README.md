# Description

The purpose of this project is to obtain granular control over the amount of noise inserted into a sound file. If one specifies a desired sound to noise ratio, the appropriate amount of noise will be inserted. Controlled noise insertion allows for testing the effectos of noise on audio in various settings.

# Instructions

- clone repo and run command ```python3 add_noise.py``` in the terminal from project root directory
- follow prompts to create the noisy audio and related visualizations
- the provided file is normalized to the RAVDESS average power level and noise is inserted based on the specified signal to noise ratio
- check the output folder for original audio, scaled(normalized) audio, noisy audio and all related visualizations

- for signal to noise ratio:
- - 0 decibels means signal power is the same as nosie power
- - -10 decibels means noise power is 10 times greater than signal power
- - 10 decibels means signal power is 10 times greater than noise power
