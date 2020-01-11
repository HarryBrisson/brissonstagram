import json
import random

import s3fs

def get_image_data():
    fs = s3fs.S3FileSystem()

    with fs.open('brissonstagram/inventory/images.json','r') as f:
        images = json.loads(f.read())

    return images
