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
    
    audio = {}
    
    def __init__(self) -> None:
        pass