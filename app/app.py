

from flask import Flask, request, render_template

from brissonstagram import *

app = Flask(__name__)


@app.route('/')
def landing():
	style = request.args.get('style')
	if not style or style=="None":
		style = "jpgs"
	data_string = get_sample_of_images(folder=style)
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
		
if __name__ == '__main__':
    app.run(debug=True)



