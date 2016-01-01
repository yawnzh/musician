from musician import Musician 
import json

with open("config.json") as f:
    config = json.load(f)

msc=Musician(config)
#msc.flush_db()
msc.fingerprint_directory('mp3',['.mp3'])
result=msc.recognize_mic(time=6,top=3)
for song,score in result:
    print("song: %s, score: %d" %(song, score))
