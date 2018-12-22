import random
import subprocess as sp

from functions.s3.s3_downloads import *
    
    
def get_random_clip_key():

    keys = get_list_of_s3_object_keys('brissonstagram',prefix='clips')
    key = random.choice(keys)
    return key

def download_random_clip():
    key = get_random_clip_key()
    download_file_from_s3('brissonstagram',key,'temp/tempvid.mp4')

def get_random_frame_from_clip(video_filename, image_filename):
    sec = random.randrange(5)
    sp.call('ffmpeg -ss 00:00:0{} -i {} -y -vframes 1 -q:v 2 {}'.format(sec,video_filename,image_filename),shell=True)


def create_boomerang_gif():

    vid_filename = "temp/tempvid.mp4"
    compressed_filename = "temp/tempsmall.mp4"
    gif_filename = "temp/tempgif.gif"

    small_cmd = 'ffmpeg -y -i {} -b 200000 {}'.format(vid_filename, compressed_filename)
    gif_maker_cmd = 'ffmpeg -y -i {} -filter_complex "[0]reverse[r];[0][r]concat,loop=1:0,setpts=N/25/TB" -f gif -pix_fmt yuv420p {}'.format(compressed_filename, gif_filename)
    sp.call(small_cmd,shell=True)
    sp.call(gif_maker_cmd,shell=True)

