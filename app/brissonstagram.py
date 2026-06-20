import json
import math
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


def parse_image_id(url):
	# urls look like .../jpgs/5b/5b-1992-0288.jpg or .../jpgs/6b/6b-0020.jpg
	# filename encodes tape-(year-)frame; frame number is the true sequence within a tape
	stem = url.split('/')[-1].rsplit('.', 1)[0]
	parts = stem.split('-')
	tape = parts[0]
	frame = int(parts[-1]) if parts[-1].isdigit() else None
	year = int(parts[1]) if len(parts) == 3 and parts[1].isdigit() else None
	return {'url': url, 'id': stem, 'tape': tape, 'frame': frame, 'year': year}


def get_random_images(folder="jpgs", n=8):
	# distinct images (no repeats) — for the memory match game
	images = get_image_data(folder=folder)
	sample = random.sample(images, min(n, len(images)))
	return [parse_image_id(i['url']) for i in sample]


def get_consecutive_frames(folder="jpgs", n=7, tape=None):
	# a run of consecutive frames from a single tape — for the sort-into-order game
	frames = [parse_image_id(i['url']) for i in get_image_data(folder=folder)]
	frames = [f for f in frames if f['frame'] is not None]

	by_tape = {}
	for f in frames:
		by_tape.setdefault(f['tape'], []).append(f)

	eligible = [t for t, fs in by_tape.items() if len(fs) >= n]
	if not eligible:
		return []
	if tape not in eligible:
		tape = random.choice(eligible)

	seq = sorted(by_tape[tape], key=lambda f: f['frame'])
	start = random.randint(0, len(seq) - n)
	return seq[start:start + n]


def hue_from_palette(palette):
	# dominant hue (0-360) from the channel weights already stored in metadata
	r, g, b = palette.get('R', 0), palette.get('G', 0), palette.get('B', 0)
	mx, mn = max(r, g, b), min(r, g, b)
	if mx == mn:
		return 0
	d = mx - mn
	if mx == r:
		h = ((g - b) / d) % 6
	elif mx == g:
		h = (b - r) / d + 2
	else:
		h = (r - g) / d + 4
	return h * 60


def get_image_metadata(folder="jpgs"):
	fs = s3fs.S3FileSystem()
	path = f'brissonstagram/inventory/{folder}-metadata.json'
	if fs.exists(path):
		with fs.open(path, 'r') as f:
			return json.loads(f.read())
	return []


def get_images_by_hue(folder="jpgs", n=160):
	# every frame ordered into a rainbow spectrum by its dominant hue
	items = []
	for m in get_image_metadata(folder=folder):
		parsed = parse_image_id(m['url'])
		parsed['hue'] = hue_from_palette(m.get('palette') or {})
		items.append(parsed)
	items.sort(key=lambda x: x['hue'])
	if n and len(items) > n:
		# even subsample keeps the full color range while capping the count
		step = len(items) / n
		items = [items[int(i * step)] for i in range(n)]
	return items


# Rekognition returns redundant synonym pairs; drop the weaker twin so the cloud reads clean
TAG_SYNONYM_DROP = {'Human', 'Apparel', 'Sports', 'People'}


def labels_for(metadata_record, conf=80):
	return [l['Name'] for l in (metadata_record.get('objects') or {}).get('Labels', [])
		if l.get('Confidence', 0) >= conf and l['Name'] not in TAG_SYNONYM_DROP]


def get_tag_counts(folder="jpgs", min_count=6, limit=70):
	# tag cloud: every Rekognition object label, sized by how often it appears
	counts = {}
	for m in get_image_metadata(folder=folder):
		for name in labels_for(m):
			counts[name] = counts.get(name, 0) + 1
	tags = [{'tag': k, 'count': v} for k, v in counts.items() if v >= min_count]
	tags.sort(key=lambda x: -x['count'])
	tags = tags[:limit]
	if tags:
		mx = tags[0]['count']
		for t in tags:
			t['size'] = round(14 + 32 * math.sqrt(t['count'] / mx))
	random.shuffle(tags)  # scramble so the cloud isn't just a sorted list
	return tags


def get_frames_with_tag(folder="jpgs", tag=None, limit=120):
	# montage: every frame whose labels include this tag
	matches = [parse_image_id(m['url']) for m in get_image_metadata(folder=folder)
		if tag in labels_for(m)]
	total = len(matches)
	if limit and total > limit:
		matches = random.sample(matches, limit)
	return matches, total


def get_year_round(folder="jpgs"):
	# guess-the-year: a dated frame plus three plausible decoy years
	dated = [f for f in (parse_image_id(i['url']) for i in get_image_data(folder=folder)) if f['year']]
	target = random.choice(dated)
	others = list({f['year'] for f in dated} - {target['year']})
	random.shuffle(others)
	options = sorted([target['year']] + others[:3])
	return {'url': target['url'], 'year': target['year'], 'options': options}


def get_river_frames(folder="jpgs", n=40):
	# timeline river: a small chronological sample of dated frames
	dated = [f for f in (parse_image_id(i['url']) for i in get_image_data(folder=folder)) if f['year']]
	sample = random.sample(dated, min(n, len(dated)))
	sample.sort(key=lambda f: (f['year'], f['tape'], f['frame'] if f['frame'] is not None else 0))
	return sample

	