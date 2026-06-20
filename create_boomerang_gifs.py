"""Generate boomerang GIFs from the S3 home-video clips.

For each 5s clip in s3://brissonstagram/clips/{tape}/, take the first 2s, build a
forward+reverse boomerang, palette-optimize, and upload a small looping GIF to
s3://brissonstagram/gifs/{tape}/. Writes an inventory/gifs.json the river reads.

Idempotent and resumable: skips clips whose GIF already exists, appends each
result to a JSONL manifest, and is single-run locked.

Usage:  python create_boomerang_gifs.py [count=1000] [workers=6]
"""

import os
import sys
import json
import time
import random
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3

BUCKET = 'brissonstagram'
TMP = 'temp/boomerang'
LOG = 'temp/boomerang_run.log'
MANIFEST = 'temp/boomerang_manifest.jsonl'
LOCK = 'temp/boomerang.lock'

# first 2s, 12fps, 320px wide, forward+reverse, palette-optimized for small clean gifs
FFMPEG_FILTER = (
	"[0:v]trim=0:2,setpts=PTS-STARTPTS,fps=12,scale=320:-1:flags=lanczos[base];"
	"[base]split[b1][b2];[b2]reverse[rev];[b1][rev]concat=n=2:v=1[bm];"
	"[bm]split[s0][s1];[s0]palettegen=stats_mode=diff[p];"
	"[s1][p]paletteuse=dither=bayer:bayer_scale=5[out]"
)

s3 = boto3.client('s3')
io_lock = threading.Lock()
counter = {'ok': 0, 'skip': 0, 'fail': 0}


def log(msg):
	line = '{} {}'.format(time.strftime('%H:%M:%S'), msg)
	print(line, flush=True)
	with open(LOG, 'a') as f:
		f.write(line + '\n')


def year_of(base):
	# base like "1-1989-0005"
	parts = base.split('-')
	if len(parts) >= 3 and parts[1].isdigit() and len(parts[1]) == 4:
		return int(parts[1])
	return None


def make_gif(inp, outp):
	cmd = ['ffmpeg', '-y', '-i', inp, '-filter_complex', FFMPEG_FILTER,
		'-map', '[out]', '-loop', '0', outp]
	subprocess.run(cmd, check=True, timeout=120,
		stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def process(clip_key, existing):
	base = clip_key.split('/')[-1].rsplit('.', 1)[0]
	tape = clip_key.split('/')[1]
	gif_key = 'gifs/{}/{}.gif'.format(tape, base)
	if gif_key in existing:
		with io_lock:
			counter['skip'] += 1
		return
	inp = '{}/{}.mp4'.format(TMP, base)
	outp = '{}/{}.gif'.format(TMP, base)
	try:
		s3.download_file(BUCKET, clip_key, inp)
		make_gif(inp, outp)
		s3.upload_file(outp, BUCKET, gif_key,
			ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/gif'})
		entry = {
			'url': 'https://{}.s3.amazonaws.com/{}'.format(BUCKET, gif_key),
			'id': base, 'tape': tape, 'year': year_of(base),
		}
		with io_lock:
			with open(MANIFEST, 'a') as f:
				f.write(json.dumps(entry) + '\n')
			counter['ok'] += 1
			n = counter['ok']
		if n % 25 == 0:
			log('progress ok={ok} skip={skip} fail={fail}'.format(**counter))
	except Exception as e:
		with io_lock:
			counter['fail'] += 1
		log('FAIL {}: {}'.format(clip_key, e))
	finally:
		for p in (inp, outp):
			try:
				os.remove(p)
			except OSError:
				pass


def list_keys(prefix, suffix):
	keys = []
	for page in s3.get_paginator('list_objects_v2').paginate(Bucket=BUCKET, Prefix=prefix):
		for o in page.get('Contents', []):
			if o['Key'].endswith(suffix):
				keys.append(o['Key'])
	return keys


def build_inventory():
	entries = {}
	if os.path.exists(MANIFEST):
		with open(MANIFEST) as f:
			for line in f:
				e = json.loads(line)
				entries[e['id']] = e
	data = list(entries.values())
	s3.put_object(Bucket=BUCKET, Key='inventory/gifs.json',
		Body=json.dumps(data), ACL='public-read', ContentType='application/json')
	log('wrote inventory/gifs.json with {} entries'.format(len(data)))


def main():
	count = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
	workers = int(sys.argv[2]) if len(sys.argv) > 2 else 6
	os.makedirs(TMP, exist_ok=True)
	if os.path.exists(LOCK):
		print('lock present at {} — another run active? remove it to proceed.'.format(LOCK))
		sys.exit(1)
	open(LOCK, 'w').close()
	try:
		log('listing clips...')
		clips = [k for k in list_keys('clips/', '.mp4')
			if year_of(k.split('/')[-1].rsplit('.', 1)[0]) is not None]
		log('{} dated clips found'.format(len(clips)))
		existing = set(list_keys('gifs/', '.gif'))
		log('{} gifs already exist (will skip)'.format(len(existing)))
		random.shuffle(clips)
		targets = clips[:count]
		log('generating up to {} boomerang gifs with {} workers'.format(len(targets), workers))
		with ThreadPoolExecutor(max_workers=workers) as ex:
			futs = [ex.submit(process, k, existing) for k in targets]
			for _ in as_completed(futs):
				pass
		log('DONE ok={ok} skip={skip} fail={fail}'.format(**counter))
		build_inventory()
	finally:
		try:
			os.remove(LOCK)
		except OSError:
			pass


if __name__ == '__main__':
	main()
