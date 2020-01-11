import random
import json
import subprocess as sp
import os

import s3fs    

def get_clip_keys(fs=None):
    if not fs:
        fs = s3fs.S3FileSystem()
    keys = fs.find(f'brissonstagram/clips')
    return keys

def download_clip(key):
    print('downloading {}'.format(key))
    fs = s3fs.S3FileSystem()
    with fs.open(key,'rb') as f:
        data = f.read()
    with open('temp/rawvid.mp4','wb') as f:
        f.write(data)


def get_random_frame_from_clip(video_filename, image_filename):
    sec = random.randrange(5)
    sp.call('ffmpeg -ss 00:00:0{} -i {} -y -vframes 1 -q:v 2 {}'.format(sec,video_filename,image_filename),shell=True)

