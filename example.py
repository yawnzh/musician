from musician import Musician
import pyaudio
import wave
import numpy as np
import redis
import timeit
from pydub import AudioSegment

msc=Musician()
if False:
    r=redis.Redis()
    r.flushdb()
    msc.fingerprint_directory('mp3',['.mp3'])

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10
 
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

sample_data=np.fromstring(b''.join(frames),np.int16)
#audiofile = AudioSegment.from_file("最佳损友 - 陈奕迅.mp3")
#if audiofile.frame_rate!=44100:
#    raise Exception("Audio sample rate must be 44.1kHz")
#audiofile=audiofile.set_channels(1)
#audiofile = audiofile[20*1000:30 * 1000]
#sample_data=data = np.fromstring(audiofile._data, np.int16)


msc.recognize_pcm(sample_data,top=10)

