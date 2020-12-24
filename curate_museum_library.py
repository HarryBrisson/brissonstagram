import s3fs


from stylize_images_as_art import *
from post_random_memory import *


def add_art_to_library(fs=None):

	if not fs:
		fs = s3fs.S3FileSystem()

	key = download_random_clip()
	clip_name = key.split('/')[-1]
	filepath = f'brissonstagram/art/{clip_name}.jpg'

	create_gram_ready_image()
	style_image_with_tensorflow_hub()

	with open('temp/artsy.jpg','rb') as f:
		img_data = f.read()
	
	with fs.open(filepath, 'wb') as f:
		f.write(img_data)

	clear_temp_folder_of_media_files()


if __name__ == "__main__":
	add_art_to_library()