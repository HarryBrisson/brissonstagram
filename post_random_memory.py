import random
import json
import subprocess as sp

import tweepy

from functions.s3.s3_downloads import *
    
    
def get_random_clip_key():

    keys = get_list_of_s3_object_keys('brissonstagram',prefix='clips')
    key = random.choice(keys)
    return key

def download_random_clip():
    key = get_random_clip_key()
    download_file_from_s3('brissonstagram',key,'temp/rawvid.mp4')

def get_random_frame_from_clip(video_filename, image_filename):
    sec = random.randrange(5)
    sp.call('ffmpeg -ss 00:00:0{} -i {} -y -vframes 1 -q:v 2 {}'.format(sec,video_filename,image_filename),shell=True)


def create_boomerang_gif(bitrate=140000, length=2, framerate=15):

    vid_filename = "temp/rawvid.mp4"
    abbrv_filename = "temp/abbrv.mp4"
    compressed_filename = "temp/compressed.mp4"
    gif_filename = "temp/gif.gif"

    compress_cmd = 'ffmpeg -y -i {} -b {} {}'.format(vid_filename, bitrate, compressed_filename)
    abbrv_cmd = 'ffmpeg -y -ss 1 -t {} -i {} {}'.format(length, compressed_filename, abbrv_filename)
    gif_maker_cmd = 'ffmpeg -y -i {} -r {} -filter_complex "[0]reverse[r];[0][r]concat,loop=1:0,setpts=N/{}/TB" -f gif {}'.format(abbrv_filename, framerate, framerate*2, gif_filename)
    sp.call(compress_cmd,shell=True)
    sp.call(abbrv_cmd,shell=True)
    sp.call(gif_maker_cmd,shell=True)



