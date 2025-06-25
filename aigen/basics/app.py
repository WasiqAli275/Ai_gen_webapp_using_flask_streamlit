from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "<p>Hello, World!, we are learning coding and this is my first flask web app.py</p>"