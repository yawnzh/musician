import redis
from collections import Counter
pool=None

def init():
    global pool
    if not pool:
        pool=redis.ConnectionPool()

def reset():
    r=redis.Redis(connection_pool=pool)
    r.flushdb()
    r.set('next_id',0)
        
def get_songs():
    pass

def has(file_hash):
    pass

def insert_song(song_name):
    r=redis.Redis(connection_pool=pool)
    sid=r.incr('next_id')
    r.hset('songs',sid,song_name)
    return sid
    
def insert_hashes(sid,hashes):
    r=redis.Redis(connection_pool=pool)
    pipe=r.pipeline()
    for h,t in hashes:
        pipe.sadd(b'fp'+h,sid<<17|0x10000|t)
    pipe.execute()
    
    
def match(hashes,top=1):
    res=[]
    r=redis.Redis(connection_pool=pool)
    for h,t in hashes: 
        matches=list(r.smembers(b'fp'+h))
        ar=[int(m)-t for m in matches]
        res+=ar
    count=Counter(res)
    top_n=count.most_common(top)
    for x in top_n:
        song_id=x[0]>>17
        name=r.hget('songs',song_id).decode('utf-8')
        yield name,x[1]
    
        