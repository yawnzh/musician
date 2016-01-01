import redis
from collections import Counter

pool=None
def init(host='localhost', port=6379, db=0):
    global pool
    if not pool:
        pool=redis.ConnectionPool(host=host, port=port, db=db)

def flush():
    r=redis.Redis(connection_pool=pool)
    r.flushdb()
    r.set('next_id',0)
        
def get_songs():
    r=redis.Redis(connection_pool=pool)
    return r.smembers('song_names')

def has(song_name):
    r=redis.Redis(connection_pool=pool)
    return r.sismember('song_names',song_name)

def insert_song(song_name):
    r=redis.Redis(connection_pool=pool)
    sid=r.incr('next_id')
    r.hset('songs',sid,song_name)
    r.sadd('song_names',song_name)
    return sid

"""
add hashes to a set
set name : b'fp:'+hash 
    value: song_id<<17|0x10000|t
we can get all the songs'id and time offsets correspond to a hash in O(1) time.
"""
def insert_hashes(sid,hashes):
    r=redis.Redis(connection_pool=pool)
    pipe=r.pipeline()
    for h,t in hashes:
        pipe.sadd(b'fp:'+h,sid<<17|0x10000|t)
    pipe.execute()
    
    
def match(hashes,top=1):
    res=[]
    r=redis.Redis(connection_pool=pool)
    for h,t in hashes: 
        matches=r.smembers(b'fp:'+h)
        ar=[int(m)-t for m in matches]
        res+=ar
    count=Counter(res)
    top_n=count.most_common(top)
    for x in top_n:
        song_id=x[0]>>17
        name=r.hget('songs',song_id).decode('utf-8')
        yield name,x[1]
    
        