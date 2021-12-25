import json
import random

import s3fs

def get_image_data(folder="jpgs",filters=None):
	fs = s3fs.S3FileSystem()

	if filters:
		image_data_path = f'brissonstagram/inventory/{folder}-metadata.json'
	else:
		image_data_path = f'brissonstagram/inventory/{folder}.json'

	if fs.exists(image_data_path):
		with fs.open(image_data_path,'r') as f:
			images = json.loads(f.read())
	else:
		if filters:
			folder = 'metadata/jpgs'
		else:
			folder = 'jpgs'
		images = create_image_inventory(folder=folder)

	if filters:

		images = [i for i in images if i.get('palette').get('complexity')>100]

		if 'red' in filters:
			images = [i for i in images if (i.get('palette').get('R')>i.get('palette').get('B')) and (i.get('palette').get('R')>i.get('palette').get('G'))]

		if 'green' in filters:
			images = [i for i in images if (i.get('palette').get('G')>i.get('palette').get('B')) and (i.get('palette').get('G')>i.get('palette').get('R'))]

		if 'blue' in filters:
			images = [i for i in images if (i.get('palette').get('B')>i.get('palette').get('R')) and (i.get('palette').get('B')>i.get('palette').get('G'))]

		if 'faces' in filters:
			images = [i for i in images if len(i.get('faces').get('FaceDetails'))>0]

	return images


def create_image_inventory(folder="jpgs"):
	fs = s3fs.S3FileSystem()
	keys = fs.find(f'brissonstagram/{folder}')
	
	data = [{'url':f'https://brissonstagram.s3.amazonaws.com/{"/".join(k.split("/")[1:])}'} for k in keys]

	with fs.open(f'brissonstagram/inventory/{folder}.json','w') as f:
		f.write(json.dumps(data))

	return data


def get_sample_of_images(folder="jpgs",n=100,force_update=False,filters=None):
	if force_update:
		create_image_inventory(folder=folder)
	images = get_image_data(folder=folder,filters=filters)
	sample = random.choices(images,k=n)
	for img in sample:
		img['id'] = img['url'].split('/')[-1].split('.')[0]
		axes = ['x','y','z']
		random.shuffle(axes)
		img[axes[0]] = (1+random.random()*.5)*random.choice([-1,1])
		img[axes[1]] = 1.5-3*random.random()
		img[axes[2]] = 1.5-3*random.random()
	return sample

	