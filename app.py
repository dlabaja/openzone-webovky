from flask import Flask, render_template, session, request
from pymongo import MongoClient
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, widgets 
from wtforms.validators import InputRequired
import pymongo
import config

app = Flask(__name__)
app.secret_key = config.secret
client = MongoClient(config.connection_string)

@app.route("/")
def index():
    return render_template("index.html.j2")

@app.route("/form", methods=['GET', 'POST'])
def form():
    form = Form()    
    if not hasVoted():
        if form.validate_on_submit():
            name = form.name.data
            choice = form.choice.data
            print(name + choice)
            #session["voted"] = True
            return render_template("form_completed.html.j2", form = form)
        return render_template("form.html.j2", form = form)
    return render_template("form_completed.html.j2", form = form)
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html.j2')

class Form(FlaskForm):
    name = StringField("Jméno", widget = widgets.Input(input_type = "text"), validators=[InputRequired("Musíte zadat jméno")])
    choice = RadioField("Vyberte možnost", choices=[("js" ,"Javascript"), ("clang", "C lang"), ("py", "Python")], validators=[InputRequired("Musíte zadat možnost")])

def hasVoted():
    for item in session:
        if item == "voted":
            return True
    return False