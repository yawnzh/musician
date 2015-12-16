import musician.fingerprinter as fingerprinter
import musician.music_library as music_library
import musician.decoder as decoder
import multiprocessing
import os
import traceback
import sys
import timeit 

class Musician(object):
    
    def __init__(self,limit=None):
        music_library.init()
        self.limit=limit
        
    def recognize_pcm(self,sample_data,top=1):
        hashes=fingerprinter.fingerprint(sample_data)
        t = timeit.Timer(lambda: music_library.match(hashes,top))
        print(t.timeit(number=1))
        for song_name, score in music_library.match(hashes,top):
            print("Song name:%s, Score: %d" %(song_name,score))
    
        
    
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
        for filename,_ in decoder.find_files(path, extensions):

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
                    sid = music_library.insert_song(song_name)
                    music_library.insert_hashes(sid, hashes)


        pool.close()
        pool.join()

    def fingerprint_file(self, filepath, song_name=None):
        songname = decoder.path_to_songname(filepath)
        song_name = song_name or songname

        song_name, hashes, file_hash = _fingerprint_worker(
            filepath,
            self.limit,
            song_name=song_name
        )
        sid = music_library.insert_song(song_name)
        music_library.insert_hashes(sid, hashes)


    
def _fingerprint_worker(filename, limit=None, song_name=None):
    try:
        filename, limit = filename
    except ValueError:
        pass
    songname, extension = os.path.splitext(os.path.basename(filename))
    song_name = song_name or songname
    sample_data=decoder.read(filename, limit)
    if sample_data is not None:
        print("Fingerprinting for %s." % (filename))
        hashes = fingerprinter.fingerprint(sample_data)
        print("%s fingerprinted." % (filename))
        return song_name,set(hashes)
    return None,None