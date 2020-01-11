

from flask import Flask, request, render_template

from brissonstagram import *

app = Flask(__name__)


@app.route('/')
def landing():
	return render_template('index.html')

		
if __name__ == '__main__':
    app.run(debug=True)



