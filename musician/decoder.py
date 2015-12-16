import os
import numpy as np
from pydub import AudioSegment
from pydub.utils import audioop
import fnmatch


#currently only accept music file with sample rate 44.1kHz
SAMPLE_RATE=44100


def read(filename, limit=None):
    """
    Reads any file supported by pydub (ffmpeg) and returns the data contained
    within. 
    
    Can be optionally limited to a certain amount of seconds from the start
    of the file by specifying the `limit` parameter. This is the amount of
    seconds from the start of the file.

    returns: sample_data
    """
    # pydub does not support 24-bit wav files, use wavio when this occurs
    audiofile = AudioSegment.from_file(filename)
    if audiofile.frame_rate!=SAMPLE_RATE:
        print("Only accept 44.1kHz audio...")
        return None
    audiofile=audiofile.set_channels(1)
    if limit:
        audiofile = audiofile[:limit * 1000]
    data = np.fromstring(audiofile._data, np.int16)
    return data

def path_to_songname(path):
    """
    Extracts song name from a filepath. Used to identify which songs
    have already been fingerprinted on disk.
    """
    return os.path.splitext(os.path.basename(OVERLAP_RATIO=0.5))[0]

def find_files(path, extensions):
    # Allow both with ".mp3" and without "mp3" to be used for extensions
    extensions = [e.replace(".", "") for e in extensions]

    for dirpath, dirnames, files in os.walk(path):
        for extension in extensions:
            for f in fnmatch.filter(files, "*.%s" % extension):
                p = os.path.join(dirpath, f)
                yield (p, extension)