import random
import json
import subprocess as sp
import os

import s3fs    

from functions.s3.s3_downloads import *

def get_clip_keys(fs=None):
    if not fs:
        fs = s3fs.S3FileSystem()
    keys = fs.find(f'brissonstagram/clips')
    return keys

