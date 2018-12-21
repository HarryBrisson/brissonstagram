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

