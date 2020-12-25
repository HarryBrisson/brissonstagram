import json
import random

import s3fs

def get_image_data(folder="jpgs"):
	fs = s3fs.S3FileSystem()

	try:
		with fs.open(f'brissonstagram/inventory/{folder}.json','r') as f:
			images = json.loads(f.read())
	except:
		images = create_image_inventory(folder=folder)

	return images

def create_image_inventory(folder="jpgs"):
	fs = s3fs.S3FileSystem()
	keys = fs.find(f'brissonstagram/{folder}')
	
	data = [{'url':f'https://brissonstagram.s3.amazonaws.com/{"/".join(k.split("/")[1:])}'} for k in keys]

	with fs.open(f'brissonstagram/inventory/{folder}.json','w') as f:
		f.write(json.dumps(data))

	return data


def get_sample_of_images(folder="jpgs",n=100,force_update=False):
	if force_update:
		create_image_inventory(folder=folder)
	images = get_image_data(folder=folder)
	sample = random.sample(images,n)
	return sample

	