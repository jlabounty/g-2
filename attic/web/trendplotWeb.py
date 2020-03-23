from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index.html')
def index2():
    return render_template('index.html')

@app.route('/generic.html')
def hello(name=None):
    return render_template('generic.html', name=name)

@app.route('/elements.html')
def elements(name=None):
    return render_template('elements.html', name=name)

@app.route('/sipmTemperatures_24h.html')
def sipm24(name=None):
    return render_template('sipmTemperatures_24h.html', name=name)

@app.route('/<path:file>')
def serve_results(file):
    return send_from_directory(app.static_folder, file)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8367)
