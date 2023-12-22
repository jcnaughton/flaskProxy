from flask import Flask
import requests

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/proxy/<server>')
def profile(server):
    url = 'http://' + server + '/'
    r=requests.get(url)
    return r.text

@app.after_request
def apply_caching(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
