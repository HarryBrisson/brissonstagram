import boto3
import json


def get_credentialed_s3_resource():

	# access credentials folder
	with open('authorizations/aws-credentials.json') as f:
		cred = json.load(f)

	# access s3 using credentials
	s3 = boto3.resource(
		's3',
		aws_access_key_id=cred["aws_access_key_id"],
		aws_secret_access_key=cred["aws_secret_access_key"]
		)

	return s3

def get_list_of_s3_object_keys(bucket,prefix=None):

	s3 = get_credentialed_s3_resource()

	if prefix:
		keys = [blob.key for blob in s3.Bucket(bucket).objects.filter(Prefix=prefix)]
	else:
		keys = [blob.key for blob in s3.Bucket(bucket).objects.all()]

	return keys


def download_file_from_s3(bucket,key,destination):
	s3 = get_credentialed_s3_resource()
	s3.Bucket(bucket).download_file(key, destination)
