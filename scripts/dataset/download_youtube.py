'''
  @ Date: 2022-03-29 13:55:42
  @ Author: Qing Shuai
  @ Mail: s_q@zju.edu.cn
  @ LastEditors: Qing Shuai
  @ LastEditTime: 2022-05-06 16:45:47
  @ FilePath: /EasyMocapPublic/scripts/dataset/download_youtube.py
'''
from glob import glob
from os.path import join
from urllib.error import URLError
from pytube import YouTube
import os
from easymocap.mytools.debug_utils import log, mkdir, myerror

extensions = ['.mp4', '.webm']

def download_youtube(vid, outdir):
    outname = join(outdir, vid)
    url = 'https://www.youtube.com/watch?v={}'.format(vid)
    for ext in extensions:
        if os.path.exists(outname+ext) and not args.restart:
            log('[Info]: skip video {}'.format(outname+ext))
            return 0
    log('[Info]: start to download video {}'.format(outname))
    log('[Info]: {}'.format(url))
    yt = YouTube(url)
    try:
        streams = yt.streams.filter(progressive=True)
    except KeyError:
        myerror('[Error]: not found streams: {}'.format(url))
        return 1
    except URLError:
        myerror('[Error]: Url error: {}'.format(url))
        return 1
    find = False
    streams_valid = streams.all()
    
    if len(streams_valid) == 0:
        for stream in streams:
            print(stream)
        myerror('[BUG ] Not found valid stream, please check the streams')
        return 0
    
    # Select the first stream available
    stream = streams_valid[0]
    title = stream.title
    res = stream.resolution
    log('[Info]: {}'.format(title))
    log('[Info]: The resolution is {}, ext={}'.format(res, stream.mime_type))
    filename = '{}.{}'.format(vid, stream.mime_type.split('/')[-1])
    try:
        stream.download(output_path=outdir, filename=filename)
        log('[Info]: Succeed')
    except:
        myerror('[BUG ]: Failed')
        return 1

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('vid', type=str)
    parser.add_argument('--database', type=str, default='data/youtube')
    parser.add_argument('--num', type=int, default=1)
    parser.add_argument('--only4k', action='store_true')
    parser.add_argument('--no720', action='store_true')
    parser.add_argument('--restart', action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    vid = args.vid
    # check database
    database = join(args.database, 'videos')
    mkdir(database)
    videonames = sorted(os.listdir(database))
    log('[download] video database in {}'.format(database))
    log('[download] already has {} videos'.format(len(videonames)))

    if vid.startswith('https'):
        vid = vid.replace('https://www.youtube.com/watch?v=', '')
        vid = vid.split('&')[0]
        print(vid)
        urls = [vid]
    elif os.path.exists(vid):
        with open(vid, 'r') as f:
            urls = f.readlines()
        urls = list(filter(lambda x:not x.startswith('#') and len(x) > 0, map(lambda x: x.strip().replace('https://www.youtube.com/watch?v=', '').split('&')[0], urls)))
        log('[download] download {} videos from {}'.format(len(urls), vid))
    else:
        urls = [vid]
    
    for url in urls:
        download_youtube(url, database)
