import musician.musician_db as db
import musician.fingerprinter as fp
import musician.decoder as dc
import multiprocessing
import os
import traceback
import sys
import pyaudio
import wave
import numpy as np
from pydub import AudioSegment
import fnmatch

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 6

class Musician(object):
    
    def __init__(self,config):
        db_config=config.get('database',{})
        db.init(**db_config)
        self.limit=config.get('limit')
        
    def recognize_raw(self,sample_data,top=1):
        hashes=fp.fingerprint(sample_data)
        return db.match(hashes,top)
    
    def flush_db(self):
        db.flush()
    
    def recognize_mic(self,time=RECORD_SECONDS,top=1):
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        print("* recording")

        frames = []

        for i in range(0, int(RATE / CHUNK * time)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        sample_data=np.fromstring(b''.join(frames),np.int16)
        
        return self.recognize_raw(sample_data,top=1)
        
    def fingerprint_directory(self, path, extensions, nprocesses=None):
            # Try to use the maximum amount of processes if not given.
            try:
                nprocesses = nprocesses or multiprocessing.cpu_count()
            except NotImplementedError:
                nprocesses = 1
            else:
                nprocesses = 1 if nprocesses <= 0 else nprocesses

            pool = multiprocessing.Pool(nprocesses)
            filenames_to_fingerprint = []
            for filename,_ in find_files(path, extensions):

                filenames_to_fingerprint.append(filename)

            # Prepare _fingerprint_worker input
            worker_input = zip(filenames_to_fingerprint,
                               [self.limit] * len(filenames_to_fingerprint))

            # Send off our tasks
            iterator = pool.imap_unordered(_fingerprint_worker,
                                           worker_input)

            # Loop till we have all of them
            while True:
                try:
                    song_name, hashes = iterator.next()
                except multiprocessing.TimeoutError:
                    continue
                except StopIteration:
                    break
                except:
                    print("Failed fingerprinting")
                    # Print traceback because we can't reraise it here
                    traceback.print_exc(file=sys.stdout)
                else:
                    if song_name and hashes:
                        sid = db.insert_song(song_name)
                        db.insert_hashes(sid, hashes)

            pool.close()
            pool.join()

    def fingerprint_file(self, filepath, song_name=None):
        songname = path_to_songname(filepath)
        song_name = song_name or songname
        if db.has(song_name):
            print("%s already fingerprinted" %(song_name))
            return None,None
        song_name, hashes = _fingerprint_worker(
            filepath,
            self.limit,
            song_name=song_name
        )
        sid = db.insert_song(song_name)
        db.insert_hashes(sid, hashes)


    
def _fingerprint_worker(filename, limit=None, song_name=None):
    try:
        filename, limit = filename
    except ValueError:
        pass
    songname, extension = os.path.splitext(os.path.basename(filename))
    song_name = song_name or songname
    if db.has(song_name):
        print("%s already fingerprinted" %(song_name))
        return None,None
    sample_data=dc.read(filename, limit)
    if sample_data is not None:
        print("Fingerprinting for %s." % (filename))
        hashes = fingerprinter.fingerprint(sample_data)
        print("%s fingerprinted." % (filename))
        return song_name,set(hashes)
    return None,None


def path_to_songname(path):
    """

    """
    return os.path.splitext(os.path.basename(path))[0]

def find_files(path, extensions):
    # Allow both with ".mp3" and without "mp3" to be used for extensions
    extensions = [e.replace(".", "") for e in extensions]

    for dirpath, dirnames, files in os.walk(path):
        for extension in extensions:
            for f in fnmatch.filter(files, "*.%s" % extension):
                p = os.path.join(dirpath, f)
                yield (p, extension)