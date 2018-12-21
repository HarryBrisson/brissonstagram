import random
import subprocess as sp

from functions.s3.s3_downloads import *
    
    
def get_random_clip_key():

    keys = get_list_of_s3_object_keys('brissonstagram',prefix='clips')
    key = random.choice(keys)
    return key

