import librosa
from typing import List, Union, Optional, Tuple
import re
import os
import soundfile as sf

class Audio:
    
    def __init__(self, include: Optional[Union[str, Tuple[str, ...]]] = None, exclude: Optional[Union[str, Tuple[str, ...]]] = None, recursive: Optional[bool] = False) -> None:
        """
        Creates a new audio object.
        
        This function can initialize a new empty object or load specific files based on the include path(s),
        exclude regex pattern(s), and the recursive directory search flag.

        Parameters
        ----------
            include (Union[str, Tuple[str, ...]]): Directories or file paths to include.
            exclude (Optional[Union[str, Tuple[str, ...]]] = None): Patterns for which matching paths are excluded.
            recursive (bool, optional): Whether to search directories recursively. Defaults to False.            
        Examples
        --------
            load 2 files and search a directory recursively while ignoring filenames containing "file1" or "file3" or "file7":
            
            >>> myaudio = Audio(include=["../audiofile1.wav", "../audiofile2.wav", "../audio_directory"],
                                exclude=[r'.*file[137].*],
                                recursive=True) 
        """
        
        self.samples = {}
        if(include):
            self.fetch(include, exclude, recursive)
    
    def fetch(self, include: Union[str, Tuple[str, ...]], exclude: Optional[Union[str, Tuple[str, ...]]] = None, recursive: bool = False, append: bool = True) -> bool:
        """
        Loads audio files. This function allows loading specific audio files or directories with optional exclusion patterns and a recursive search option.
        It can either append files to an existing audio_samples dictionary or overwrite it.

        Parametrs
        ---------
            include (Union[str, Tuple[str, ...]]): Directories or file paths to include.
            exclude (Optional[Union[str, Tuple[str, ...]]] = None): Patterns for which matching paths are excluded.
            recursive (bool, optional): Whether to search directories recursively. Defaults to False.
            append (bool, optional): True to add new files to the existing dictionary, False to overwrite. Defaluts to True.

        Returns
        -------
            bool: True if all files loaded successfully, False otherwise.
        
        Examples
        --------
            load 2 files and search a directory recursively while ignoring filenames containing "file1" or "file3" or "file7":
            
            >>> myaudio = Audio(include=["../audiofile1.wav", "../audiofile2.wav", "../audio_directory"],
                                exclude=[r'.*file[137].*],
                                recursive=True)
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
                print(f"{path} matched a pattern in the exclude list and was ignored.")
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
                    self.samples[f.split('/')[-1]] = [sample, sr]
                except Exception as e:
                    print(f"Error loading {f}: {e}.")
                    return False
        
        return True
    
    def _fetch_from_directory(self, directory: str, exclude: Tuple[re.Pattern, ...], recursive: bool) -> List[str]:
        """
        Fetch files from a directory based on include and exclude patterns and recursive search flag.

        Parameters
        ----------
            directory (str): The directory to search.
            exclude (Tuple[re.Pattern, ...]): Tuple of regex patterns to exclude.
            recursive (bool): Boolean indicating whether to search directories recursively.

        Returns
        -------
            List[str]: List of files meeting criteria.
        """
        
        directory = directory if directory.endswith('/') else (directory + '/')
        extensions = ["*.wav", "*.mp3", "*.flac", "*.ogg", "*.m4a", "*.aac", "*.wma", "*.aiff", "*.au", "*.amr",]  # Supported audio formats
        
        audio_files = []
        
        iteration = 0
        for root, dirs, files in os.walk(directory):

            iteration += 1            

            for file in files:
                file_path = os.path.join(root, file)
                if not self._is_excluded(file_path, exclude) and any(file_path.endswith(ext[1:]) for ext in extensions):
                    audio_files.append(file_path)

            if not recursive and iteration > 0:
                break
            
            # Exclude directories early
            dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d), exclude)]
                    
        return audio_files
   
    def _is_excluded(self, file_path: str, exclude: Tuple[re.Pattern, ...]) -> bool:
        """
        Check if a file path matches any of the excluded regex patterns.

        Parameters
        ----------
            file_path (str): The file path to check.
            exclude (Tuple[re.Pattern, ...]): Tuple of regex patterns to exclude.
        
        Returns
        -------
            bool: Boolean indicating whether or not the file path is excluded.
        """
        
        for e in exclude:
            if(e.search(file_path)):
                return True
        return False
    
    def write(self, output_path: str, in_place: Optional[bool] = False) -> bool:
        """
        Writes current state of audio samples to a specified directory. Automatically places output in a new "output" folder or overwrites existing files.

        Parameters
        ----------
            output_path (str): Path of directory in which to write currently loaded audio files.
            in_place (bool, optional): True to overwrite existing files, False to place output in new folder. Defaults to False.
        
        Returns
        -------
            bool: Boolean indicating whether or not all file(s) were written successfully.
        """
        
        if not os.path.isdir(output_path):
            print(f"{output_path} is either not a directory or doesn't exist.")
            return False
        
        if not in_place:
            output_path = output_path+"output/" if output_path.endswith('/') else (output_path+'/output/')
            if not os.path.isdir(output_path):
                os.mkdir(output_path)

        for file in self.samples.keys():
            sf.write(os.path.join(output_path,file), self.samples[file][0], self.samples[file][1])
            

    def print(self) -> None:
        """
        Displays the current state of the samples dictionary. Shows file path as key and list containing details of loaded sample array
        and sample rate as value.
        """
        count = 0
        print("{")
        if len(self.samples.keys()) != 0:
            for key in self.samples.keys():
                if (count == (len(self.samples.keys())-1) ):
                    print(f"{key} : [ (dtype={self.samples[key][0].dtype}, shape=|{self.samples[key][0].shape}), sample_rate={self.samples[key][1]} ]")
                else:
                    print(f"{key} : [ (dtype={self.samples[key][0].dtype}, shape={self.samples[key][0].shape}), sample_rate={self.samples[key][1]} ],")
                count += 1
        print("}")