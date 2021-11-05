from flask import Flask, render_template
import random

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html.j2")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html.j2')



