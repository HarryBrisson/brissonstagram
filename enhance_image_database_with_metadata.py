import json
import random

import s3fs
from PIL import Image
import requests
import boto3


def get_palette_characteristics(img_path):

	img = Image.open(requests.get(img_path, stream=True).raw)

	color_frequency = img.histogram()

	palette_characteristics = {}

	for i in range(3):
		color = 'RGB'[i]
		palette_characteristics[color] = sum([f*n for f, n in enumerate(color_frequency[i*256:(i+1)*256])])

	palette_characteristics['complexity'] = sum([f > 0 for f in color_frequency])

	return palette_characteristics



def get_credentialed_rekognition_resource():

	# access credentials folder
	with open('authorizations/aws-credentials.json') as f:
		cred = json.load(f)

	# access rekognition using credentials
	client = boto3.client(
		'rekognition',
		aws_access_key_id=cred["aws_access_key_id"],
		aws_secret_access_key=cred["aws_secret_access_key"]
		)

	return client


def get_labels_for_image(img_path,client=None):

	if not client:
		client = get_credentialed_rekognition_resource()

	bucket = img_path.split('//')[1].split('.')[0]
	name = img_path.split('amazonaws.com/')[1]

	response = client.detect_labels(
	    Image={
	        'S3Object': {
	            'Bucket': bucket,
	            'Name': name,
		        }
		    },
		)

	return response


def get_faces_for_image(img_path,client=None):

	if not client:
		client = get_credentialed_rekognition_resource()

	bucket = img_path.split('//')[1].split('.')[0]
	name = img_path.split('amazonaws.com/')[1]

	response = client.detect_faces(
	    Image={
	        'S3Object': {
	            'Bucket': bucket,
	            'Name': name,
		        }
		    },
		)

	return response



def get_metadata_for_image(img_path,client=None,fs=None):

	if not fs:
		fs = s3fs.S3FileSystem()

	metadata_path = img_path.replace('https://','').replace('jpgs','metadata/jpgs').replace('.s3.amazonaws.com','').replace('.jpg','.json')

	if fs.exists(metadata_path):
		with fs.open(metadata_path) as f:
			metadata = json.loads(f.read())

	else:
		if not client:
			client = get_credentialed_rekognition_resource()

		palette_characteristics = get_palette_characteristics(img_path)
		object_labels = get_labels_for_image(img_path,client=client)
		face_labels = get_faces_for_image(img_path,client=client)

		metadata = {
			'url':img_path,
			'palette':palette_characteristics,
			'objects':object_labels,
			'faces':face_labels
		}

		with fs.open(metadata_path,'w') as f:
			f.write(json.dumps(metadata))

	return metadata


def get_metadata_for_images(folder="jpgs",n=1000,forceRefresh=False):

	fs = s3fs.S3FileSystem()

	metadata_path = f'brissonstagram/inventory/{folder}-metadata.json'

	if fs.exists(metadata_path) and not forceRefresh:

		with fs.open(metadata_path) as f:
			metadata = json.loads(f.read())

	else:
		with fs.open(f'brissonstagram/inventory/{folder}.json','r') as f:
			images = json.loads(f.read())

		sample = random.sample(images,n)
		metadata = []

		for i in sample:
			print(i)
			m = get_metadata_for_image(i.get('url'))
			metadata.append(m)

		with fs.open(metadata_path,'w') as f:
			f.write(json.dumps(metadata))

	return metadata


if __name__ == "__main__":
	get_metadata_for_images(n=10000,forceRefresh=True)