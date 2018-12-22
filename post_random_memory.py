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


def create_gram_ready_video():
    
    vid_filename = "temp/rawvid.mp4"
    square_filename = "temp/square.mp4"
    gram_ready_filename = "temp/gram_ready.mp4"

    square_cmd = 'ffmpeg -y -i {} -vf "crop=\'min(iw,1*ih)\':\'min(iw/1,ih)\',scale=720:720" {}'.format(vid_filename, square_filename)
    boomerang_cmd = 'ffmpeg -y -i {} -filter_complex "[0]reverse[r];[0][r]concat,loop=1:0,setpts=N/25/TB" {}'.format(square_filename, gram_ready_filename)
    sp.call(square_cmd,shell=True)
    sp.call(boomerang_cmd,shell=True)


def tweet_boomerang_gif(status=''):

    cred = json.loads(open('authorizations/twitter-credentials.json').read())
    
    auth = tweepy.OAuthHandler(cred['CONSUMER_KEY'], cred['CONSUMER_SECRET'])
    auth.set_access_token(cred['ACCESS_TOKEN'], cred['ACCESS_TOKEN_SECRET'])
    api = tweepy.API(auth)

    gif = api.media_upload('temp/gif.gif')
    api.update_status(status=status,media_ids=[gif.media_id])