from flask import Flask, render_template, session, request
import random
import config

app = Flask(__name__)
app.secret_key = config.secret

#git test
#jinja-html v include, hodnota html, inc-lan

@app.route("/")
def index():
    return render_template("index.html.j2")

@app.route("/t")
def test():
    name = request.args.get("name")
    password = request.args.get("password")
    if name:
        session["cookie"] = name,password
    print(session)
    return render_template("test.html.j2"), session

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html.j2')



