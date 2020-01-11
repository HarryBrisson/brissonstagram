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

def create_gram_ready_image():

    print('creating gram-friendly square video')
    
    vid_filename = "temp/rawvid.mp4"
    square_vid_filename = "temp/square.mp4"
    square_image_filename = "temp/square_raw.mp4"
    compressed_filename = "temp/square.jpg"

    square_cmd = 'ffmpeg -y -i {} -vf "crop=\'min(iw,1*ih)\':\'min(iw/1,ih)\',scale=720:720" {}'.format(vid_filename, square_vid_filename)
    compress_cmd = 'ffmpeg -y -i {} -compression_level 50 {}'.format(square_image_filename, compressed_filename)
    
    sp.call(square_cmd,shell=True)
    get_random_frame_from_clip(square_vid_filename, square_image_filename)
    sp.call(compress_cmd,shell=True)


