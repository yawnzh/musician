import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import generate_binary_structure, \
    iterate_structure, binary_erosion
import struct

FRAME_RATE=44100
WINDOW_SIZE=4096
OVERLAP_RATIO=0.5
TIME_FUZ_FACTOR=2
FREQUENCE_FUZ_FACTOR=2
DEFAULT_FAN_VALUE=15
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 150
IDX_FREQ_I = 0
IDX_TIME_J = 1
PEAK_NEIGHBORHOOD_SIZE=40

def fingerprint(sample_data):
    spec,f,t = mlab.specgram(sample_data,
                     NFFT=WINDOW_SIZE,
                     Fs=FRAME_RATE,
                     window=mlab.window_hanning,
                     noverlap=int(WINDOW_SIZE * OVERLAP_RATIO))
    spec=spec[f<5000]
    spec[spec==0]=0.1**10 
    spec=10*np.log10(spec)
    peaks=get_2D_peaks(spec,plot=False)
    return generate_hashes(peaks)

def get_2D_peaks(arr2D, plot=False):
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

    # find local maxima using our fliter shape

    local_max = maximum_filter(arr2D, size=(20,40)) == arr2D
    background = arr2D == 0

    # Boolean mask of arr2D with True at peaks

    detected_peaks = local_max - background
    
    amps = arr2D[detected_peaks]
    (j, i) = np.where(detected_peaks)
    amps = amps.flatten()
    amp_min=10
    peaks = zip(i, j, amps)
    peaks_filtered = [x for x in peaks if x[2] > amp_min]  
    frequency_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]
    if plot:
        (fig, ax) = plt.subplots()
        ax.imshow(arr2D)
        ax.scatter(time_idx, frequency_idx)
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title('Spectrogram')
        ax.set_aspect('auto')
        plt.gca().invert_yaxis() 
        plt.show()
    return list(zip(frequency_idx, time_idx))
ANCHOR_OFFSET=3

def generate_hashes(peaks, fan_value=DEFAULT_FAN_VALUE):
    """
    hash value: 32 bit unsigned integer
    0-7 bit: t_delta
    8-15 bit: freq2
    16-23 bit: freq1
    """
    peaks.sort(key=lambda p:(p[1],p[0]))
    
    for i in range(len(peaks)):
        for j in range(ANCHOR_OFFSET, ANCHOR_OFFSET+fan_value):
            if i + j< len(peaks):
                freq1 = peaks[i][IDX_FREQ_I]//FREQUENCE_FUZ_FACTOR
                freq2 = peaks[i + j][IDX_FREQ_I]//FREQUENCE_FUZ_FACTOR
                t1 = peaks[i][IDX_TIME_J]
                t2 = peaks[i + j][IDX_TIME_J]
                t_delta = (t2 - t1)//TIME_FUZ_FACTOR

                if t_delta >= MIN_HASH_TIME_DELTA and t_delta \
                    <= MAX_HASH_TIME_DELTA:
                    h=((freq1&0xfff)<<20)|((freq2&0xfff)<<8)|(t_delta&0xff)
                    h=struct.pack('>I',h)
                    yield (h, t1)