

from flask import Flask, request, render_template

from brissonstagram import *

app = Flask(__name__)


@app.route('/')
def landing():
	style = request.args.get('style')
	filters = request.args.get('filters')
	if not style or style=="None":
		style = "jpgs"
	if filters=='None':
		filters=None
	data_string = get_sample_of_images(folder=style, filters=filters)
	html = render_template('index.html',
		data_string = data_string)
	return html

@app.route('/vr')
def vr():
	style = request.args.get('style')
	if not style or style=="None":
		style = "jpgs"
	data_string = get_sample_of_images(folder=style)
	print(data_string)
	html = render_template('museum.html',
		data_string = data_string)
	return html

@app.route('/spectrum')
def spectrum():
	data_string = get_images_by_hue()
	return render_template('spectrum.html', data_string=data_string)

@app.route('/match')
def match():
	pairs = int(request.args.get('pairs', 8))
	data_string = get_random_images(n=pairs)
	return render_template('match.html', data_string=data_string)

@app.route('/sort')
def sort():
	n = int(request.args.get('n', 7))
	data_string = get_consecutive_frames(n=n)
	return render_template('sort.html', data_string=data_string)

@app.route('/tags')
def tags():
	tag = request.args.get('tag')
	if tag:
		frames, total = get_frames_with_tag(tag=tag)
		return render_template('tags.html', tag=tag, data_string=frames, total=total)
	return render_template('tags.html', tag=None, cloud=get_tag_counts())

@app.route('/river')
def river():
	# send a chronological pool; the options panel renders a live subset of it
	n = int(request.args.get('n', 40))
	data_string = get_river_frames(n=n)
	return render_template('river.html', data_string=data_string)

@app.route('/guess')
def guess():
	data_string = get_year_round()
	return render_template('guess.html', data_string=data_string)

if __name__ == '__main__':
    import os
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)))



