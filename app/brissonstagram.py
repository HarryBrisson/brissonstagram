import json
import random

import s3fs

def get_image_data():
	fs = s3fs.S3FileSystem()

	try:
		with fs.open('brissonstagram/inventory/images.json','r') as f:
			images = json.loads(f.read())
	except:
		images = create_image_inventory()

	return images

def create_image_inventory():
	fs = s3fs.S3FileSystem()
	keys = fs.find('brissonstagram/jpgs')
	
	data = [{'url':f'https://brissonstagram.s3.amazonaws.com/{"/".join(k.split("/")[1:])}'} for k in keys]

	with fs.open('brissonstagram/inventory/images.json','w') as f:
		f.write(json.dumps(data))

	return data


def get_sample_of_images(n=100):
    images = get_image_data()
    sample = random.sample(images,n)

    