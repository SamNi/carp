import sys
import os.path
import cPickle as pickle
import bz2
from urllib import urlretrieve

import pytumblr as pyt
import credentials as cred

dbfilename = 'posts.bz2'
debugInfo = True
target = ''

def dbg(msg):
    if not debugInfo:
        return
    sys.stderr.write(str(msg) + '\n')

def main():
    if os.path.exists(dbfilename):
        dbg(dbfilename + " exists, loading")
        fin = bz2.BZ2File(dbfilename, 'rb')
        seenPosts = pickle.load(fin)
        fin.close()
    else:
        dbg("starting over from scratch")
        seenPosts = set()
    if not os.path.exists(target):
        os.mkdir(target)
        dbg('Directory ' + target + " doesn't exist so I'm going to create it")
    client = pyt.TumblrRestClient(cred.api_key)
    offset = 0
    numImages = numPosts = 0
    while True:
        params = { 'offset': offset }
        posts = client.posts(target, **params)['posts']
        total_posts = len(posts)
        if (total_posts == 0):
            break
        offset += total_posts
        for post in posts:
            if post['type'] != 'photo':
                continue
            post_id = post['id']
            if post_id in seenPosts:
                dbg("Already have this one, skipping")
                continue
            dbg(post_id)
            for photo in post['photos']:
                imgurl = photo['original_size']['url']
                imgfilename = os.path.basename(imgurl)
                dbg(imgfilename)
                urlretrieve(imgurl, os.path.join(target, imgfilename))
                numImages += 1
            seenPosts.add(post_id)
            numPosts += 1
        pickle.dump(seenPosts, bz2.BZ2File(dbfilename, 'wb'))
    dbg("Saved %d new images across %d new posts " % (numImages, numPosts))

if __name__ == '__main__':
    sys.exit( main() )