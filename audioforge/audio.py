import librosa
from typing import List, Union, Optional, Tuple
import re
import os
import glob
import numpy as np

# the main audio class will create audio objects that will store numpy arrays and sample rates of one or more audio files
# the user can:
    # specify the path to one file
    # specify the path to a folder containing multiple sound files
    # specify a list of paths to multiple individual files or folders containing files
        # everything in a folder will be included by default
        # use a regex string to select specific files in a folder

    # provide a list of files to ignore (none by default)
    # provide a list of folder paths to ignore (everything ignored by default - overrides include)
    # use regex to specify particular name patterns to ignore

class Audio:
    
    def __init__(self, include: Union[str, Tuple[str, ...]], exclude: Optional[Union[str, Tuple[str, ...]]] = None, recursive: bool = False) -> None:
        """
        Create new audio object initidalized with a dictionary of audio_samples loaded using files from specified directories
        given include and exclude patterns.

        :param include: A string or tuple of strings specifying the directories or patterns to include.
        :param exclude: A string or set of strings specifying the patterns to exclude.
        :param recursive: Boolean indicating whether to search directories recursively.
        """
        
        self.samples = {}
        self.fetch(include, exclude, recursive)
    
    def fetch(self, include: Union[str, Tuple[str, ...]], exclude: Optional[Union[str, Tuple[str, ...]]] = None, recursive: bool = False, append=False) -> bool:
        """
        Fetch files from specified directories with include and exclude patterns.

        :param include: A string or tuple of strings specifying the directories or patterns to include.
        :param exclude: A string or set of strings specifying the patterns to exclude.
        :param recursive: Boolean indicating whether to search directories recursively.
        :param append: True for adding new files to the existing audio dictionary, or False to overwrite it.
        :return: Boolean value True if all files loaded successfully, False otherwise.
        """
        if isinstance(include, str):
            include = (include,)
            
        if exclude is None:
            exclude = ()
        elif isinstance(exclude, str):
            exclude = (re.compile(exclude),)
        elif isinstance(exclude, tuple):
            try:
                exclude = tuple([re.compile(r) for r in exclude])
            except Exception as e:
                print("Please ensure only strings are used as the exclude patterns.")
                return False

        audio_files = []
        
        for path in include:
            if(self._is_excluded(path, exclude)):
                print(f"{path} matched a pattern in the exclude list and was ignored")
                continue
            if os.path.isdir(path):
                audio_files.extend(self._fetch_from_directory(path, exclude, recursive))
            elif os.path.isfile(path):
                audio_files.append(path)
            else:
                print(f"{path} does not exist or is not a regular file/directory.")
        
        # Clearing the samples dictionary if append = False
        if(not append):
            self.samples.clear()
        
        # check for existence before loading
        for f in audio_files:
            if(f in self.samples.keys()):
                continue
            else:
                try:
                    sample, sr = librosa.load(f)
                    self.samples[f] = [sample, sr]
                except Exception as e:
                    print(f"Error loading {f}: {e}")
                    return False
        
        return True
    
    def _fetch_from_directory(self, directory: str, exclude: Tuple[re.Pattern, ...], recursive: bool) -> List[str]:
        """
        Fetch files from a directory based on include and exclude patterns.

        :param directory: The directory to search.
        :param exclude: Set of regex patterns to exclude.
        :param recursive: Boolean indicating whether to search directories recursively.
        :return: List of file paths.
        """
        
        directory = directory if directory.endswith('/') else (directory + '/')
        extensions = ["*.wav", "*.mp3", "*.flac", "*.ogg", "*.m4a", "*.aac", "*.wma", "*.aiff", "*.au", "*.amr",]  # Supported audio formats
        
        paths = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                # Exclude directories early
                dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d), exclude)]
                for file in files:
                    file_path = os.path.join(root, file)
                    if not self._is_excluded(file_path, exclude) and any(file_path.endswith(ext[1:]) for ext in extensions):
                        paths.append(file_path)
        else:
            for ext in extensions:
                search_pattern = directory + ext
                for path in glob.iglob(search_pattern, recursive=False):
                    if not self._is_excluded(path, exclude):
                        paths.append(path)
                    
        return paths
   
    def _is_excluded(self, file_path: str, exclude: Tuple[re.Pattern, ...]) -> bool:
        """
        Check if a file path matches any of the exclude patterns.

        :param file_path: The file path to check.
        :param exclude: Set of regex patterns to exclude.
        :return: Boolean indicating whether the file path is excluded.
        """
        
        # use regex or regular wildcard expressions for better exclusion matching
        for e in exclude:
            if(e.search(file_path)):
                return True
        return False

    def print(self) -> None:
        """
        Displays the current state of the samples dictionary. Outputs the audio file path as the key and a list containing details of loaded amplitude
        numpy array along with the sample rate.
        """
        count = 0
        print("{")
        if len(self.samples.keys()) != 0:
            for key in self.samples.keys():
                if (count == (len(self.samples.keys())-1) ):
                    print(f"{key} : [ (len={self.samples[key][0].size}, dtype={self.samples[key][0].dtype}, shape={self.samples[key][0].shape}), sample_rate={self.samples[key][1]} ]")
                else:
                    print(f"{key} : [ (len={self.samples[key][0].size}, dtype={self.samples[key][0].dtype}, shape={self.samples[key][0].shape}), sample_rate={self.samples[key][1]} ],")
                count += 1
        print("}")