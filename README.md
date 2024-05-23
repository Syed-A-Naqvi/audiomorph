# Description

The purpose of this project is to obtain granular control over the amount of noise inserted into a sound file. One can specify the desired sound to noise ratio and the appropriate amount of white noise will be inserted into the sound file. Controlled noise insertion allows for testing the effectos of noise on audio in various settings.

# Instructions

- clone repo and run the command ```python3 add_noise.py <audio_file>``` in the terminal from the project root directory
- replace ```<audio_file>``` with the name of the ravdess audio file to modify
- provide the desired signal to noise ratio in decibals:
- - 0 decibals means equal signal to noise
- - 10 decibals means signal is 10 times as powerful as noise
- - -10 decibals means noise is 10 times as powerful as signal

- the provided file is normalized and noise is inserted based on the specified signal to noise ratio
- check the output folder for original audio, scaled(normalized) audio and finally the noisy audio
