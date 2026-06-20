

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

if __name__ == '__main__':
    import os
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)))



