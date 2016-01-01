import os
import numpy as np
from pydub import AudioSegment
from pydub.utils import audioop
import fnmatch


#currently only accept music file with sample rate 44.1kHz
ACCEPTED_RATES=[44100]

def read(filename, limit=None):
    """
    
    """
    audiofile = AudioSegment.from_file(filename)
    if audiofile.frame_rate not in ACCEPTED_RATES:
        print("Not supported file :%s" %(filename))
        return None
    audiofile=audiofile.set_channels(1)
    if limit:
        audiofile = audiofile[limit * 1000:]
    data = np.fromstring(audiofile._data, np.int16)
    return data

