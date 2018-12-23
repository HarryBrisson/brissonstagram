import random
import json
import subprocess as sp

import tweepy

from functions.s3.s3_downloads import *
from functions.send_attachment import *
    
    
def get_random_clip_key():
    print('accessing list of all clips')
    keys = get_list_of_s3_object_keys('brissonstagram',prefix='clips')
    print('selecting random clip')
    key = random.choice(keys)
    return key

def download_random_clip():
    key = get_random_clip_key()
    print('downloading {}'.format(key))
    download_file_from_s3('brissonstagram',key,'temp/rawvid.mp4')

def get_random_frame_from_clip(video_filename, image_filename):
    sec = random.randrange(5)
    sp.call('ffmpeg -ss 00:00:0{} -i {} -y -vframes 1 -q:v 2 {}'.format(sec,video_filename,image_filename),shell=True)


def create_boomerang_gif(bitrate=140000, length=2, framerate=15):

    print('creating {}s {}fps boomerang gif w/ {} bitrate'.format(length,framerate,bitrate))

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

    print('creating gram-friendly square video')
    
    vid_filename = "temp/rawvid.mp4"
    square_filename = "temp/square.mp4"
    reverse_filename = "temp/reverse.mp4"
    gram_ready_filename = "temp/gram_ready.mp4"

    square_cmd = 'ffmpeg -y -i {} -vf "crop=\'min(iw,1*ih)\':\'min(iw/1,ih)\',scale=720:720" {}'.format(vid_filename, square_filename)
    reverse_cmd = 'ffmpeg -y -i {} -vf reverse -af areverse {}'.format(square_filename, reverse_filename)
    boomerang_cmd = 'ffmpeg -y -i {} -i {} -filter_complex "[0:v] [0:a] [1:v] [1:a] concat=n=2:v=1:a=1 [v] [a]" -map "[v]" -map "[a]" {}'.format(square_filename, reverse_filename, gram_ready_filename)
    
    sp.call(square_cmd,shell=True)
    sp.call(reverse_cmd,shell=True)
    sp.call(boomerang_cmd,shell=True)


def tweet_media(media_filepath,status=''):

    print('accessing Twitter credentials')
    cred = json.loads(open('authorizations/twitter-credentials.json').read())
    
    print('logging into Twitter')
    auth = tweepy.OAuthHandler(cred['CONSUMER_KEY'], cred['CONSUMER_SECRET'])
    auth.set_access_token(cred['ACCESS_TOKEN'], cred['ACCESS_TOKEN_SECRET'])
    api = tweepy.API(auth)

    print('uploading media')
    gif = api.media_upload('media_filepath')
    print('posting tweet')
    api.update_status(status=status,media_ids=[gif.media_id])

def post_random_memory():
    download_random_clip()
    create_boomerang_gif()
    tweet_boomerang_gif()
    create_gram_ready_video()
    send_attachment_over_email(
        'brissonstagram@gmail.com', ['ejbrisson@gmail.com'],
        'Brissonstagram Video', 'temp/gram_ready.mp4'
    )


if __name__ == '__main__':
    post_random_memory()
