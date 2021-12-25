import json

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

	return s3


def get_labels_for_image(img_path,client=None):

	if not client:
		client = get_credentialed_rekognition_resource()

	bucket = img_path.split('//')[1].split('.')[0]
	name = img_path.split('amazon.com/')[1]

	response = client.detect_labels(
	    Image={
	        'S3Object': {
	            'Bucket': bucket,
	            'Name': name,
		        }
		    },
		)

	return response


def get_metadata_for_image(img_path):

	palette_characteristics = get_palette_characteristics(img_path)
	object_labels = get_labels_for_image(img_path)
	print(object_labels)


def get_metadata_for_images(folder="jpgs"):

	fs = s3fs.S3FileSystem()

	with fs.open(f'brissonstagram/inventory/{folder}.json','r') as f:
		images = json.loads(f.read())

	for i in images:
		get_metadata_for_image(i.get('url'))
	
	return images


if __name__ == "__main__":
	get_metadata_for_images()