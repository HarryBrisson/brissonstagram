

from flask import Flask, request, render_template

from brissonstagram import *

app = Flask(__name__)


@app.route('/')
def landing():
	data_string = get_sample_of_images()
	html = render_template('index.html',
		data_string = data_string)
	return html

		
if __name__ == '__main__':
    app.run(debug=True)



