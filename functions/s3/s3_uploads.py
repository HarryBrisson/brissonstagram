import os

import boto3


def add_file_to_s3(file,bucket,destination):

	# access credentials folder
	with open('authorizations/aws-credentials.json') as f:
		cred = json.load(f)

	# access s3 using credentials
	s3 = boto3.resource(
		's3',
		aws_access_key_id=cred["aws_access_key_id"],
		aws_secret_access_key=cred["aws_secret_access_key"]
		)

	# save file to s3
	print('...opening')
	data = open(file, 'rb')
	print('...uploading')
	s3.Bucket(bucket).put_object(Key=destination, Body=data)