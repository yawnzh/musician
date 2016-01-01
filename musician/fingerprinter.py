import matplotlib
matplotlib.use('TkAgg')
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import maximum_filter
import struct

FRAME_RATE=44100
WINDOW_SIZE=4096
OVERLAP_RATIO=0.5
TIME_FUZ_FACTOR=2
FREQUENCE_FUZ_FACTOR=2
BACKGROUND_FACTOR=0.65

MIN_DELTA_TIME=0
MAX_DELTA_TIME=250


DEFAULT_FAN_VALUE=10

ANCHOR_OFFSET=3
"""
input:  sampled audio data
output: (frequency, time) pairs
"""
def fingerprint(sample_data):
    spec,f,t = mlab.specgram(sample_data,
                     NFFT=WINDOW_SIZE,
                     Fs=FRAME_RATE,
                     window=mlab.window_hanning,
                     noverlap=int(WINDOW_SIZE * OVERLAP_RATIO))
    # keep freqencies below 5000
    spec=spec[f<5000]
    spec[spec==0]=0.1**10 
    spec=10*np.log10(spec)
    times,frequencies=get_peaks(spec)
    if False:
        fig, ax = plt.subplots()
        ax.imshow(spec)
        ax.scatter(times, frequencies)
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title('Spectrogram')
        ax.set_aspect('auto')
        plt.gca().invert_yaxis() 
        plt.show()
    return generate_hashes(times,frequencies)
    

def get_peaks(spec,size=(25,35)):
    filter=maximum_filter(spec, size=size) == spec
    amp_min=BACKGROUND_FACTOR * np.mean(spec[filter])
    print("amp_min: %d" %(amp_min))
    background_filter= spec>=max(10,amp_min)
    peaks_filter=np.logical_and(filter,background_filter)
    peaks_filter=np.transpose(peaks_filter)
    times,frequencies=np.where(peaks_filter)
    print("number of hashes: %d" %(len(times)))
    return times,frequencies
    

def generate_hashes(ts,fs,fan_value=DEFAULT_FAN_VALUE):
    for i in range(len(ts)):
        for j in range(ANCHOR_OFFSET, ANCHOR_OFFSET+fan_value):
            if i+j<len(ts):
                f1=fs[i]//FREQUENCE_FUZ_FACTOR
                f2=fs[i+j]//FREQUENCE_FUZ_FACTOR
                t1=ts[i]//TIME_FUZ_FACTOR
                delta_t=(ts[i+j]-ts[i])//TIME_FUZ_FACTOR
                if delta_t>=MIN_DELTA_TIME and delta_t<=MAX_DELTA_TIME:
                    h=((f1&0xfff)<<20)|((f2&0xfff)<<8)|(delta_t&0xff)
                    h=struct.pack('>I',h)
                    yield (h, t1)
                
    
    
    