from flask import Flask, render_template
import collector.collect_server as c
# from .collector.collect_server import get_samples
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello world"

@app.route('/data')
def getData():
    return "[" + c.get_samples(600, 200).strip(",") +"]"

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

if __name__ == '__main__':
    app.run(debug=True)