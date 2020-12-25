import s3fs
from PIL import Image

from stylize_images_as_art import *
from post_random_memory import *


def check_for_palette_complexity(image_path):

	img = Image.open(image_path)

	color_frequency = img.histogram()

	colors_represented = sum([f > 0 for f in color_frequency])

	return colors_represented



def add_art_to_library(fs=None):

	if not fs:
		fs = s3fs.S3FileSystem()

	key = download_random_clip()
	clip_name = key.split('/')[-1].split('.')[0]

	create_gram_ready_image()

	colors_included = check_for_palette_complexity('temp/square.png')
	print(colors_included)

	if colors_included > 50:

		data = style_image_with_tensorflow_hub()

		style_path = data['style']
		style = style_path.split('/')[-1].split('.')[0]

		print(style)

		filepath = f'brissonstagram/art/{clip_name}--{style}.jpg'

		with open('temp/artsy.jpg','rb') as f:
			img_data = f.read()
		
		with fs.open(filepath, 'wb') as f:
			f.write(img_data)

	clear_temp_folder_of_media_files()


if __name__ == "__main__":
	for i in range(100):
		add_art_to_library()